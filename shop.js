const CART_STORAGE_KEY = "petshop_cart";
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const productGrid = document.querySelector("#product-grid");
const cartPanel = document.querySelector("#cart-panel");
const toast = document.querySelector("#shop-toast");
const productImages = {
  racao: "photo-1589924691995-400dc9ECC119",
  "petisco": "photo-1601758228041-f3b2795255f1",
  "higiene": "photo-1583337130417-3346a1be7dee",
  acessorios: "photo-1548199973-03cce0bbc87b",
  "brinquedos": "photo-1535294435445-d7249524ef2e"
};
let products = [];
let cart = readCart();
let activeCategory = "todos";
let toastTimer;

function readCart() {
  const saved = localStorage.getItem(CART_STORAGE_KEY);
  if (!saved) return [];
  try {
    const parsed = JSON.parse(saved);
    if (!Array.isArray(parsed)) throw new Error("Formato da sacola inválido.");
    const quantities = new Map();
    parsed.forEach((item) => {
      if (
        item && Number.isSafeInteger(item.id) && item.id > 0 &&
        Number.isSafeInteger(item.quantidade) && item.quantidade > 0 && item.quantidade <= 99
      ) {
        quantities.set(item.id, Math.min(99, (quantities.get(item.id) || 0) + item.quantidade));
      }
    });
    return Array.from(quantities, ([id, quantidade]) => ({ id, quantidade }));
  } catch (error) {
    console.error("Não foi possível recuperar a sacola salva.", error);
    localStorage.removeItem(CART_STORAGE_KEY);
    return [];
  }
}

function saveCart() {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
  renderCart();
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 2600);
}

function normalizeText(value) {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
}

function productImageUrl(category) {
  const photoId = productImages[normalizeText(category)] || productImages.acessórios;
  return `https://images.unsplash.com/${photoId}?auto=format&fit=crop&w=700&q=80`;
}

function renderFilters() {
  const filterList = document.querySelector("#filter-list");
  const categories = [...new Set(products.map((product) => product.categoria).filter(Boolean))];
  filterList.replaceChildren();

  [["todos", "Todos"], ...categories.map((category) => [category, category])].forEach(([value, label]) => {
    const button = document.createElement("button");
    button.className = `filter-button${value === activeCategory ? " active" : ""}`;
    button.type = "button";
    button.dataset.category = value;
    button.setAttribute("aria-pressed", String(value === activeCategory));
    button.textContent = label;
    filterList.append(button);
  });
}

function createProductCard(product) {
  const card = document.createElement("article");
  card.className = "product-card";

  const imageArea = document.createElement("div");
  imageArea.className = "product-image";
  const placeholder = document.createElement("span");
  placeholder.className = "product-placeholder";
  placeholder.setAttribute("aria-hidden", "true");
  placeholder.textContent = "🐾";
  const image = document.createElement("img");
  image.src = product.imagem || productImageUrl(product.categoria);
  image.alt = product.nome;
  image.loading = "lazy";
  image.addEventListener("error", () => { image.hidden = true; }, { once: true });
  imageArea.append(placeholder, image);

  if (product.estoque <= 3) {
    const stockTag = document.createElement("span");
    stockTag.className = "product-tag";
    stockTag.textContent = product.estoque === 1 ? "Última unidade" : `${product.estoque} unidades`;
    imageArea.append(stockTag);
  }

  const info = document.createElement("div");
  info.className = "product-info";
  const category = document.createElement("span");
  category.className = "product-category";
  category.textContent = product.categoria || "Para seu pet";
  const name = document.createElement("h3");
  name.textContent = product.nome;
  const purchase = document.createElement("div");
  purchase.className = "product-purchase";
  const price = document.createElement("span");
  price.className = "product-price";
  price.textContent = money.format(product.preco);
  const addButton = document.createElement("button");
  addButton.className = "add-to-cart";
  addButton.type = "button";
  addButton.dataset.action = "add";
  addButton.dataset.id = product.id;
  addButton.setAttribute("aria-label", `Adicionar ${product.nome} à sacola`);
  addButton.textContent = "+";
  purchase.append(price, addButton);
  info.append(category, name, purchase);
  card.append(imageArea, info);
  return card;
}

function renderProducts() {
  const search = normalizeText(document.querySelector("#product-search").value.trim());
  const visibleProducts = products.filter((product) => {
    const matchesCategory = activeCategory === "todos" || product.categoria === activeCategory;
    const matchesSearch = !search || normalizeText(`${product.nome} ${product.categoria}`).includes(search);
    return matchesCategory && matchesSearch;
  });

  productGrid.replaceChildren();
  if (visibleProducts.length === 0) {
    const empty = document.createElement("p");
    empty.className = "no-products";
    empty.textContent = products.length ? "Nenhum produto encontrado com esses filtros." : "Não há produtos disponíveis no momento.";
    productGrid.append(empty);
  } else {
    visibleProducts.forEach((product) => productGrid.append(createProductCard(product)));
  }
  document.querySelector("#product-count").textContent = `${visibleProducts.length} ${visibleProducts.length === 1 ? "produto" : "produtos"}`;
  productGrid.setAttribute("aria-busy", "false");
}

function renderCart() {
  const cartItems = document.querySelector("#cart-items");
  const cartCount = cart.reduce((total, item) => total + item.quantidade, 0);
  const productsById = new Map(products.map((product) => [product.id, product]));
  const availableItems = cart.filter((item) => productsById.has(item.id));
  const subtotal = availableItems.reduce((total, item) => {
    const product = productsById.get(item.id);
    return total + product.preco * item.quantidade;
  }, 0);
  const validCart = cart.length > 0 && availableItems.length === cart.length &&
    cart.every((item) => item.quantidade <= productsById.get(item.id).estoque && item.quantidade <= 99);

  document.querySelector("#cart-count").textContent = cartCount;
  document.querySelector("#cart-total").textContent = money.format(subtotal);
  const checkoutLink = document.querySelector("#checkout-link");
  checkoutLink.classList.toggle("is-disabled", !validCart);
  checkoutLink.setAttribute("aria-disabled", String(!validCart));
  cartItems.replaceChildren();

  if (cart.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-cart";
    empty.textContent = "Sua sacola está esperando por você.";
    cartItems.append(empty);
    return;
  }

  cart.forEach((item) => {
    const product = productsById.get(item.id);
    const row = document.createElement("div");
    row.className = "cart-item";
    const description = document.createElement("div");
    const name = document.createElement("div");
    name.className = "cart-item-name";
    name.textContent = product ? product.nome : "Produto indisponível";
    const price = document.createElement("div");
    price.className = "cart-item-price";
    price.textContent = product ? money.format(product.preco * item.quantidade) : "Remova para continuar";
    description.append(name, price);
    const controls = document.createElement("div");
    controls.className = "cart-quantity";
    controls.setAttribute("aria-label", `Quantidade de ${product ? product.nome : "produto"}`);
    const decrement = document.createElement("button");
    decrement.type = "button";
    decrement.dataset.action = "decrement";
    decrement.dataset.id = item.id;
    decrement.setAttribute("aria-label", "Diminuir quantidade");
    decrement.textContent = "−";
    const quantity = document.createElement("span");
    quantity.textContent = item.quantidade;
    const increment = document.createElement("button");
    increment.type = "button";
    increment.dataset.action = "increment";
    increment.dataset.id = item.id;
    increment.setAttribute("aria-label", "Aumentar quantidade");
    increment.textContent = "+";
    increment.disabled = !product || item.quantidade >= Math.min(product.estoque, 99);
    controls.append(decrement, quantity, increment);
    row.append(description, controls);
    cartItems.append(row);

    if (product && item.quantidade > product.estoque) {
      const warning = document.createElement("p");
      warning.className = "cart-stock-warning";
      warning.textContent = `Disponíveis agora: ${product.estoque}. Ajuste a quantidade para continuar.`;
      cartItems.append(warning);
    }
  });
}

async function loadProducts() {
  try {
    const response = await fetch("/api/produtos");
    const data = await response.json();
    if (!response.ok) throw new Error(data.erro || "Não foi possível carregar os produtos.");
    if (!Array.isArray(data.produtos)) throw new Error("A vitrine recebeu uma resposta inválida.");
    products = data.produtos;
    renderFilters();
    renderProducts();
    renderCart();
  } catch (error) {
    console.error("Falha ao carregar os produtos da loja.", error);
    productGrid.replaceChildren();
    const message = document.createElement("p");
    message.className = "no-products";
    message.textContent = "Não foi possível carregar a vitrine agora. Atualize a página para tentar novamente.";
    productGrid.append(message);
    document.querySelector("#product-count").textContent = "Produtos indisponíveis";
    productGrid.setAttribute("aria-busy", "false");
    renderCart();
  }
}

document.querySelector("#filter-list").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-category]");
  if (!button) return;
  activeCategory = button.dataset.category;
  renderFilters();
  renderProducts();
});

document.querySelector("#product-search").addEventListener("input", renderProducts);

document.querySelector("#product-grid").addEventListener("click", (event) => {
  const button = event.target.closest('button[data-action="add"]');
  if (!button) return;
  const product = products.find((item) => item.id === Number(button.dataset.id));
  if (!product) {
    showToast("Este produto não está disponível no momento.");
    return;
  }
  const item = cart.find((entry) => entry.id === product.id);
  if ((item?.quantidade || 0) >= Math.min(product.estoque, 99)) {
    showToast("Você já adicionou todas as unidades disponíveis.");
    return;
  }
  if (item) item.quantidade += 1;
  else cart.push({ id: product.id, quantidade: 1 });
  saveCart();
  showToast(`${product.nome} adicionado à sacola.`);
});

document.querySelector("#cart-items").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const productId = Number(button.dataset.id);
  const item = cart.find((entry) => entry.id === productId);
  if (!item) return;
  const product = products.find((entry) => entry.id === productId);
  if (button.dataset.action === "increment" && product && item.quantidade < Math.min(product.estoque, 99)) {
    item.quantidade += 1;
  } else if (button.dataset.action === "decrement") {
    item.quantidade -= 1;
    if (item.quantidade === 0) cart = cart.filter((entry) => entry.id !== productId);
  }
  saveCart();
});

document.querySelector("#cart-toggle").addEventListener("click", () => {
  const open = cartPanel.hidden;
  cartPanel.hidden = !open;
  document.querySelector("#cart-toggle").setAttribute("aria-expanded", String(open));
});

function closeCart() {
  cartPanel.hidden = true;
  document.querySelector("#cart-toggle").setAttribute("aria-expanded", "false");
}

document.querySelector("#cart-close").addEventListener("click", closeCart);
document.querySelector("#checkout-link").addEventListener("click", (event) => {
  if (event.currentTarget.getAttribute("aria-disabled") === "true") {
    event.preventDefault();
    showToast(cart.length ? "Revise a disponibilidade dos itens na sua sacola." : "Adicione um produto antes de continuar.");
  }
});

document.querySelector("#menu-toggle").addEventListener("click", (event) => {
  const button = event.currentTarget;
  const nav = document.querySelector("#main-nav");
  const open = nav.classList.toggle("is-open");
  button.setAttribute("aria-expanded", String(open));
  button.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
});

document.querySelector("#main-nav").addEventListener("click", (event) => {
  if (!event.target.closest("a")) return;
  document.querySelector("#main-nav").classList.remove("is-open");
  document.querySelector("#menu-toggle").setAttribute("aria-expanded", "false");
});

document.querySelector("#categorias").addEventListener("click", (event) => {
  const link = event.target.closest("a[data-filter]");
  if (!link) return;
  const category = products.find((product) => product.categoria === link.dataset.filter)?.categoria;
  if (!category) return;
  activeCategory = category;
  renderFilters();
  renderProducts();
});

document.addEventListener("click", (event) => {
  if (!cartPanel.hidden && !cartPanel.contains(event.target) && !event.target.closest("#cart-toggle")) closeCart();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeCart();
    document.querySelector("#main-nav").classList.remove("is-open");
    document.querySelector("#menu-toggle").setAttribute("aria-expanded", "false");
  }
});

window.addEventListener("storage", (event) => {
  if (event.key !== CART_STORAGE_KEY) return;
  cart = readCart();
  renderCart();
});

renderCart();
loadProducts();
