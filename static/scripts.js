document.addEventListener('DOMContentLoaded', function () {
    // Обработка модального окна для регистрации
    const openRegisterModalBtn = document.querySelector('#open-register-modal');
    const registerModal = document.querySelector('#register-modal');
    const closeRegisterModalBtn = document.querySelector('#close-register-modal');
  
    openRegisterModalBtn.addEventListener('click', function () {
      registerModal.style.display = 'block';
    });
  
    closeRegisterModalBtn.addEventListener('click', function () {
      registerModal.style.display = 'none';
    });
  
    // Обработка модального окна для входа
    const openLoginModalBtn = document.querySelector('#open-login-modal');
    const loginModal = document.querySelector('#login-modal');
    const closeLoginModalBtn = document.querySelector('#close-login-modal');
  
    openLoginModalBtn.addEventListener('click', function () {
      loginModal.style.display = 'block';
    });
  
    closeLoginModalBtn.addEventListener('click', function () {
      loginModal.style.display = 'none';
    });
  
    // Функция для отправки данных формы с помощью AJAX (регистрация)
    const registerForm = document.querySelector('#register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(registerForm);
        const response = await fetch('/register', {
          method: 'POST',
          body: formData,
        });
  
        if (response.ok) {
          window.location.href = '/';  // Перенаправляем на главную страницу
        } else {
          alert('Ошибка при регистрации');
        }
      });
    }
  
    // Функция для отправки данных формы с помощью AJAX (вход)
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(loginForm);
        const response = await fetch('/login', {
          method: 'POST',
          body: formData,
        });
  
        if (response.ok) {
          window.location.href = '/';  // Перенаправляем на главную страницу
        } else {
          alert('Ошибка при входе');
        }
      });
    }
  
    // Динамическая загрузка постов (пагинация)
    let page = 1;
  
    async function loadPosts() {
      const response = await fetch(`/posts?page=${page}`);
      const data = await response.json();
  
      const postsContainer = document.querySelector('#posts-container');
      data.posts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.classList.add('post', 'fade');
        postElement.innerHTML = `
          <h2>${post.title}</h2>
          <p>${post.content}</p>
        `;
        postsContainer.appendChild(postElement);
      });
  
      page += 1;
    }
  
    document.querySelector('#load-more').addEventListener('click', function () {
      loadPosts();  // Загружаем больше постов
    });
  
    // Плавное появление элементов
    const fadeElements = document.querySelectorAll('.fade');
    fadeElements.forEach(element => {
      element.style.transition = 'opacity 0.5s ease';
      element.style.opacity = 0;
      
      setTimeout(() => {
        element.style.opacity = 1;
      }, 100);
    });
  
    loadPosts();  // Загружаем посты при загрузке страницы
  });
  