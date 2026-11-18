const CART_STORAGE_KEY = "petshop_cart";
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const deliveryForm = document.querySelector("#delivery-form");
const cartItemsElement = document.querySelector("#checkout-items");
const feedbackElement = document.querySelector("#checkout-feedback");
const resultElement = document.querySelector("#payment-result");
const brickContainer = document.querySelector("#cardPaymentBrick_container");
let cartItems = [];
let quote;
let mercadoPago;
let brickController;
let mercadoPagoUnavailableMessage = "O pagamento online está temporariamente indisponível. Tente novamente mais tarde.";
let quoteReady;
let mercadoPagoReady;
let requestInProgress = false;
let idempotencyKey = sessionStorage.getItem("petshop_checkout_idempotency");
if (!idempotencyKey) {
  idempotencyKey = crypto.randomUUID();
  sessionStorage.setItem("petshop_checkout_idempotency", idempotencyKey);
}

function showFeedback(message, target = feedbackElement) {
  target.textContent = message;
}

function getCustomerData() {
  if (!deliveryForm.reportValidity()) {
    throw new Error("Confira os dados obrigatórios antes de continuar.");
  }
  const formData = new FormData(deliveryForm);
  return {
    nome: formData.get("nome").trim(),
    email: formData.get("email").trim(),
    telefone: formData.get("telefone").trim(),
    cpf_pix: formData.get("cpf_pix").trim(),
    endereco: {
      cep: formData.get("cep").trim(),
      rua: formData.get("rua").trim(),
      numero: formData.get("numero").trim(),
      complemento: formData.get("complemento").trim(),
      bairro: formData.get("bairro").trim(),
      cidade: formData.get("cidade").trim(),
      estado: formData.get("estado").trim().toUpperCase()
    }
  };
}

function renderOrderSummary() {
  document.querySelector("#checkout-total").textContent = money.format(quote.total);
  cartItemsElement.replaceChildren();
  quote.itens.forEach((item) => {
    const row = document.createElement("div");
    row.className = "summary-item";
    const description = document.createElement("div");
    const name = document.createElement("div");
    name.className = "summary-item-name";
    name.textContent = item.nome;
    const quantity = document.createElement("div");
    quantity.className = "summary-item-quantity";
    quantity.textContent = `Quantidade: ${item.quantidade}`;
    description.append(name, quantity);
    const price = document.createElement("span");
    price.className = "summary-item-price";
    price.textContent = money.format(item.subtotal);
    row.append(description, price);
    cartItemsElement.append(row);
  });
}

async function loadQuote() {
  const rawCart = localStorage.getItem(CART_STORAGE_KEY);
  if (!rawCart) throw new Error("Sua sacola está vazia. Volte à loja e escolha seus produtos.");
  let parsedCart;
  try {
    parsedCart = JSON.parse(rawCart);
  } catch {
    localStorage.removeItem(CART_STORAGE_KEY);
    throw new Error("Não foi possível ler sua sacola. Volte à loja e monte o pedido novamente.");
  }
  if (!Array.isArray(parsedCart) || parsedCart.length === 0) {
    throw new Error("Sua sacola está vazia. Volte à loja e escolha seus produtos.");
  }
  cartItems = parsedCart;
  const response = await fetch("/api/checkout/quote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ carrinho: cartItems })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.erro || "Não foi possível carregar os preços do pedido.");
  quote = data;
  renderOrderSummary();
}

async function loadMercadoPagoConfig() {
  try {
    const response = await fetch("/api/checkout/config");
    if (!response.ok) throw new Error("Não foi possível carregar a configuração do pagamento.");
    const config = await response.json();
    if (!config.public_key) throw new Error("Credenciais do Mercado Pago não configuradas.");
    mercadoPago = new MercadoPago(config.public_key, { locale: "pt-BR" });
  } catch (error) {
    mercadoPagoUnavailableMessage = "PIX e cartão ainda não estão configurados pela loja. Entre em contato para concluir o pedido.";
    console.error("Credenciais do Mercado Pago indisponíveis.", error);
  }
}

async function destroyCardBrick() {
  if (!brickController) return;
  await brickController.unmount();
  brickController = undefined;
}

async function showCardBrick() {
  await Promise.all([quoteReady, mercadoPagoReady]);
  document.querySelector("#card-payment-area").hidden = false;
  document.querySelector("#pix-payment-area").hidden = true;
  document.querySelector("#cash-payment-area").hidden = true;
  resultElement.hidden = true;
  feedbackElement.textContent = "";
  if (!mercadoPago) {
    const notice = document.querySelector("#card-gateway-notice");
    notice.textContent = mercadoPagoUnavailableMessage;
    notice.hidden = false;
    return;
  }
  document.querySelector("#card-gateway-notice").hidden = true;
  if (!quote) {
    showFeedback("Não foi possível carregar os valores da sacola. Volte à loja e tente novamente.");
    return;
  }
  if (brickController) return;
  try {
    const bricksBuilder = mercadoPago.bricks();
    brickController = await bricksBuilder.create("cardPayment", "cardPaymentBrick_container", {
      initialization: { amount: quote.total },
      callbacks: {
        onReady: () => {},
        onSubmit: async (cardData) => {
          const customer = getCustomerData();
          const result = await submitOrder("cartao", customer, cardData);
          await showPaymentResult(result);
        },
        onError: (error) => {
          console.error("Erro no formulário seguro do Mercado Pago.", error);
          showFeedback("O formulário de cartão não pôde ser carregado. Tente novamente.");
        }
      }
    });
  } catch (error) {
    console.error("Falha ao inicializar o formulário de cartão do Mercado Pago.", error);
    showFeedback("Não foi possível carregar o formulário do cartão. Atualize a página ou escolha outra forma de pagamento.");
  }
}

async function submitOrder(paymentMethod, customer = getCustomerData(), cardData = null) {
  if (requestInProgress) throw new Error("Seu pedido já está sendo processado.");
  requestInProgress = true;
  feedbackElement.textContent = "";
  try {
    const response = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...customer,
        pagamento: paymentMethod,
        carrinho: cartItems,
        idempotency_key: idempotencyKey,
        cartao: cardData ? {
          token: cardData.token,
          payment_method_id: cardData.payment_method_id || cardData.paymentMethodId,
          issuer_id: cardData.issuer_id || cardData.issuerId,
          installments: cardData.installments,
          payer: cardData.payer
        } : null
      })
    });
    const data = await response.json();
    idempotencyKey = crypto.randomUUID();
    sessionStorage.setItem("petshop_checkout_idempotency", idempotencyKey);
    if (!response.ok) throw new Error(data.erro || "Não foi possível finalizar seu pedido.");
    return data;
  } finally {
    requestInProgress = false;
  }
}

async function showPaymentResult(result) {
  await destroyCardBrick();
  document.querySelector("#card-payment-area").hidden = true;
  document.querySelector("#pix-payment-area").hidden = true;
  document.querySelector("#cash-payment-area").hidden = true;
  resultElement.hidden = false;
  resultElement.replaceChildren();
  const heading = document.createElement("h3");
  heading.textContent = result.pix ? "PIX gerado!" : "Pedido recebido! 🐾";
  const message = document.createElement("p");
  message.textContent = result.pix
    ? "Escaneie o QR Code ou copie o código abaixo para pagar."
    : `Pedido ${result.pedido} · ${result.status_pagamento || result.status}.`;
  resultElement.append(heading, message);

  if (result.pix?.manual) {
    const pix = document.createElement("div");
    pix.className = "pix-result";

    const image = document.createElement("img");
    image.src = result.pix.qr_code_url;
    image.alt = "QR Code PIX da Pata & Companhia";

    const total = document.createElement("p");
    total.textContent = "Valor do pedido: " + money.format(result.total);

    const instruction = document.createElement("p");
    instruction.textContent =
        "Escaneie o QR Code pelo aplicativo do seu banco. Após pagar, aguarde a confirmação da loja.";

    pix.append(image, total, instruction);
    resultElement.append(pix);
}

  deliveryForm.querySelectorAll('input[name="pagamento"]').forEach((input) => { input.disabled = true; });
  localStorage.removeItem(CART_STORAGE_KEY);
  sessionStorage.removeItem("petshop_checkout_idempotency");
  cartItems = [];
}

document.querySelectorAll('input[name="pagamento"]').forEach((input) => {
  input.addEventListener("change", async () => {
    try {
      await mercadoPagoReady;
      await destroyCardBrick();
      document.querySelector('[name="cpf_pix"]').required = input.value === "pix";
      document.querySelector("#card-payment-area").hidden = true;
      document.querySelector("#pix-payment-area").hidden = input.value !== "pix";
      document.querySelector("#cash-payment-area").hidden = input.value !== "dinheiro";
      resultElement.hidden = true;
      feedbackElement.textContent = "";
      document.querySelector("#card-gateway-notice").hidden = true;
      document.querySelector("#pix-gateway-notice").hidden = true;

      if (input.value === "cartao") await showCardBrick();
    } catch (error) {
      console.error("Não foi possível alterar a forma de pagamento.", error);
      showFeedback("Não foi possível carregar essa forma de pagamento. Tente novamente.");
    }
  });
});

document.querySelector("#pix-submit").addEventListener("click", async () => {
    try {
        await quoteReady;
        await showPaymentResult(await submitOrder("pix"));
    } catch (error) {
        showFeedback(error.message);
    }
});

document.querySelector("#cash-submit").addEventListener("click", async () => {
  try {
    await showPaymentResult(await submitOrder("dinheiro"));
  } catch (error) {
    showFeedback(error.message);
  }
});

document.querySelector("#delivery-form").addEventListener("input", (event) => {
  if (event.target.name === "estado") event.target.value = event.target.value.toUpperCase();
});

quoteReady = loadQuote().catch((error) => {
    console.error("Falha ao preparar a sacola para o checkout.", error);
    cartItemsElement.replaceChildren();
    const message = document.createElement("p");
    message.className = "summary-empty";
    message.textContent = error.message;
    cartItemsElement.append(message);
    document.querySelectorAll(".payment-choice").forEach((choice) => { choice.hidden = true; });
  });
mercadoPagoReady = loadMercadoPagoConfig();
