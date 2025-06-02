console.log("scripts.js cargado correctamente.");

let carrito = JSON.parse(localStorage.getItem("carrito") || "[]");

function cerrarModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    modal.setAttribute('tabindex', '-1');
    document.body.classList.remove('modal-open');
    const modalBackdrop = document.querySelector('.modal-backdrop');
    if (modalBackdrop) modalBackdrop.remove();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const storedMode = localStorage.getItem('theme') || 'light';
  document.body.classList.add(storedMode + '-mode');
  const modeToggle = document.getElementById('modeToggle');
  if (modeToggle) {
    modeToggle.innerText = storedMode === 'dark' ? '☀ Claro' : '🌙 Oscuro';
  }

  document.querySelectorAll('.product-image').forEach(img => {
    img.addEventListener('click', function () {
      const modal = document.getElementById('myModal');
      if (modal) {
        modal.style.display = 'block';
        document.getElementById('modalImg').src = this.dataset.img;
        document.getElementById('modalTitle').innerText = this.dataset.name;
        document.getElementById('modalPrice').innerText = "Precio: $" + this.dataset.price;
      }
    });
  });

  const closeModalBtn = document.querySelector('.close-modal');
  if (closeModalBtn) {
    closeModalBtn.onclick = function () {
      const modal = document.getElementById('myModal');
      if (modal) modal.style.display = 'none';
    };
  }

  window.onclick = function (event) {
    const modal = document.getElementById('myModal');
    const confirmModal = document.getElementById('confirmModal');
    if (event.target === modal) modal.style.display = 'none';
    if (event.target === confirmModal) confirmModal.style.display = 'none';
  };

  const searchInput = document.getElementById('busqueda');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const filtro = this.value.toLowerCase();
      document.querySelectorAll('.product-row').forEach(row => {
        const nombre = row.dataset.name.toLowerCase();
        row.style.display = nombre.includes(filtro) ? '' : 'none';
      });
    });
  }

  const formCrearCuenta = document.getElementById('formCrearCuenta');
  if (formCrearCuenta) {
    formCrearCuenta.addEventListener('submit', function (e) {
      e.preventDefault();

      const password1 = formCrearCuenta.querySelector('input[name="password"]').value;
      const password2 = formCrearCuenta.querySelector('input[name="confirm_password"]').value;

      if (password1 !== password2) {
        alert('❌ Las contraseñas no coinciden.');
        return;
      }

      const formData = new FormData(formCrearCuenta);
      fetch('/admin_empleado/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
      })
      .then(res => res.ok ? res.text() : Promise.reject('Error al crear usuario'))
      .then(() => {
        document.getElementById('mensajeResultado').innerHTML = `<p>Cuenta creada con éxito.</p>`;
        new bootstrap.Modal(document.getElementById('resultadoModal')).show();
        cerrarModal('confirmModal');
        cerrarModal('crearCuentaModal');
        setTimeout(() => location.reload(), 1500);
      })
      .catch(err => alert('❌ Error: ' + err));
    });
  }
});

function toggleMode() {
  const isDark = document.body.classList.contains('dark-mode');
  document.body.classList.toggle('dark-mode', !isDark);
  document.body.classList.toggle('light-mode', isDark);
  const modeToggle = document.getElementById('modeToggle');
  if (modeToggle) {
    modeToggle.innerText = isDark ? '🌙 Oscuro' : '☀ Claro';
  }
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
}

function confirmLogout() {
  if (confirm("¿Estás seguro que deseas cerrar sesión?")) {
    window.location.href = "/cerrar_sesion/";
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function addProduct(prodId, name, price, img) {
  const idNum = parseInt(prodId.replace('prod', ''));
  const seleccionada = document.getElementById('prov' + idNum);
  if (seleccionada) seleccionada.innerText++;
  updateTotal();

  const safeImg = typeof img === "string" ? encodeURI(img) : '';

  const item = carrito.find(p => p.id === idNum);
  if (item) {
    item.cantidad++;
  } else {
    carrito.push({ id: idNum, nombre: name, precio: price, img: safeImg, cantidad: 1 });
  }
  localStorage.setItem("carrito", JSON.stringify(carrito));
  updateCarrito();
}

function removeProduct(prodId) {
  const idNum = parseInt(prodId.replace('prod', ''));
  const seleccionada = document.getElementById('prov' + idNum);
  if (seleccionada && parseInt(seleccionada.innerText) > 0) {
    seleccionada.innerText--;
    updateTotal();

    const index = carrito.findIndex(p => p.id === idNum);
    if (index !== -1) {
      carrito[index].cantidad--;
      if (carrito[index].cantidad === 0) carrito.splice(index, 1);
      localStorage.setItem("carrito", JSON.stringify(carrito));
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

  const totalSum = document.getElementById('totalSum');
  if (totalSum) {
    totalSum.innerText = total.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });
  }
}

function updateCarrito() {
  const container = document.getElementById('carritoItems');
  if (!container) return;

  container.innerHTML = '';
  let total = 0;

  carrito.forEach(p => {
    const subtotal = p.precio * p.cantidad;
    total += subtotal;

    container.innerHTML += `
      <tr>
        <td><img src="${p.img}" width="60" style="border-radius: 4px;"></td>
        <td>${p.nombre}</td>
        <td>${p.cantidad}</td>
        <td>${subtotal.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' })}</td>
      </tr>
    `;
  });

  const carritoTotal = document.getElementById('carritoTotal');
  if (carritoTotal) {
    carritoTotal.innerText = total.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });
  }
}

function toggleCarrito() {
  const modal = document.getElementById('carritoModal');
  if (modal) {
    modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
  }
}

function mostrarConfirmacion() {
  if (carrito.length === 0) {
    alert('El carrito está vacío');
    return;
  }
  const modal = document.getElementById('confirmModal');
  if (modal) modal.style.display = 'block';
}

function confirmarCompra() {
  if (carrito.length === 0) {
    alert("El carrito está vacío");
    return;
  }

  const codigo = Math.floor(100000 + Math.random() * 900000);
  console.log(">> Intentando guardar carrito con código:", codigo);

  fetch('/guardar_carrito/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ codigo: codigo, carrito: carrito })
  })
  .then(response => response.json())
  .then(data => {
    console.log(">> Respuesta del servidor:", data);
    if (data.success) {
      document.getElementById('confirmModal').style.display = 'none';

      localStorage.removeItem('carrito');
      carrito.length = 0;
      updateCarrito();
      updateTotal();
      document.querySelectorAll('span[id^="prov"]').forEach(span => span.innerText = '0');

      window.location.href = `/boleta/${codigo}/`;
    } else {
      alert('❌ Error: ' + data.error);
    }
  })
  .catch(error => {
    console.error('Error al guardar carrito:', error);
    alert('Error de red o del servidor.');
  });
}
