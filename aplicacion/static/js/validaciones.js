console.log("scripts.js cargado correctamente.");

let carrito = [];

document.addEventListener('DOMContentLoaded', () => {
  const storedMode = localStorage.getItem('theme') || 'dark';
  document.body.classList.add(storedMode + '-mode');
  document.getElementById('modeToggle').innerText = storedMode === 'dark' ? '☀ Claro' : '🌙 Oscuro';

  document.querySelectorAll('.product-image').forEach(img => {
    img.addEventListener('click', function () {
      document.getElementById('myModal').style.display = 'block';
      document.getElementById('modalImg').src = this.dataset.img;
      document.getElementById('modalTitle').innerText = this.dataset.name;
      document.getElementById('modalPrice').innerText = "Precio: $" + this.dataset.price;
    });
  });

  document.querySelector('.close-modal').onclick = function () {
    document.getElementById('myModal').style.display = 'none';
  };

  window.onclick = function (event) {
    if (event.target === document.getElementById('myModal')) {
      document.getElementById('myModal').style.display = 'none';
    }
    if (event.target === document.getElementById('confirmModal')) {
      document.getElementById('confirmModal').style.display = 'none';
    }
  };

  document.getElementById('busqueda').addEventListener('input', function () {
    const filtro = this.value.toLowerCase();
    document.querySelectorAll('.product-row').forEach(row => {
      const nombre = row.dataset.name.toLowerCase();
      row.style.display = nombre.includes(filtro) ? '' : 'none';
    });
  });
});

function toggleMode() {
  const isDark = document.body.classList.contains('dark-mode');
  document.body.classList.toggle('dark-mode', !isDark);
  document.body.classList.toggle('light-mode', isDark);
  document.getElementById('modeToggle').innerText = isDark ? '🌙 Oscuro' : '☀ Claro';
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
}

function confirmLogout() {
  if (confirm("¿Estás seguro que deseas cerrar sesión?")) {
    window.location.href = "/cerrar_sesion/";
  }
}

function addProduct(prodId, name, price, img) {
  const disponible = document.getElementById(prodId);
  const seleccionada = document.getElementById('prov' + prodId.replace('prod', ''));

  if (parseInt(disponible.innerText) > 0) {
    disponible.innerText--;
    seleccionada.innerText++;
    updateTotal();

    const staticImg = img.startsWith('/static/') ? img : '/static/' + img;

    const item = carrito.find(p => p.id === prodId);
    if (item) {
      item.cantidad++;
    } else {
      carrito.push({ id: prodId, name, price, img: staticImg, cantidad: 1 });
    }
    updateCarrito();
  }
}

function removeProduct(prodId) {
  const disponible = document.getElementById(prodId);
  const seleccionada = document.getElementById('prov' + prodId.replace('prod', ''));

  if (parseInt(seleccionada.innerText) > 0) {
    disponible.innerText++;
    seleccionada.innerText--;
    updateTotal();

    const index = carrito.findIndex(p => p.id === prodId);
    if (index !== -1) {
      carrito[index].cantidad--;
      if (carrito[index].cantidad === 0) carrito.splice(index, 1);
      updateCarrito();
    }
  }
}

function updateTotal() {
  let total = 0;
  document.querySelectorAll('tbody tr').forEach(row => {
    const priceCell = row.querySelector('.price-cell');
    if (!priceCell) return;

    const price = parseFloat(priceCell.dataset.price);
    const qtyEl = row.querySelector('span[id^="prov"]');
    if (!qtyEl) return;

    const qty = parseInt(qtyEl.innerText);
    const totalCell = row.querySelector('.row-total');
    const rowTotal = price * qty;

    if (totalCell) {
      totalCell.innerText = rowTotal.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });
    }

    total += rowTotal;
  });

  document.getElementById('totalSum').innerText = total.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });
}

function updateCarrito() {
  const container = document.getElementById('carritoItems');
  container.innerHTML = '';
  let total = 0;

  carrito.forEach(p => {
    const subtotal = p.price * p.cantidad;
    total += subtotal;

    container.innerHTML += `
      <tr>
        <td><img src="${p.img}" width="60" style="border-radius: 4px;"></td>
        <td>${p.name}</td>
        <td>${p.cantidad}</td>
        <td>${subtotal.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' })}</td>
      </tr>
    `;
  });

  document.getElementById('carritoTotal').innerText = total.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });
}

function toggleCarrito() {
  const modal = document.getElementById('carritoModal');
  modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
}

function mostrarConfirmacion() {
  if (carrito.length === 0) {
    alert('El carrito está vacío');
    return;
  }
  document.getElementById('confirmModal').style.display = 'block';
}

function confirmarCompra() {
  carrito.forEach(p => {
    const disponible = document.getElementById(p.id);
    const cantidad = parseInt(disponible.innerText);
    disponible.innerText = cantidad - p.cantidad;

    const seleccionada = document.getElementById('prov' + p.id.replace('prod', ''));
    seleccionada.innerText = '0';
  });

  alert('✅ Venta efectuada con éxito.');
  carrito = [];
  updateCarrito();
  updateTotal();
  document.getElementById('carritoModal').style.display = 'none';
  document.getElementById('confirmModal').style.display = 'none';
}
