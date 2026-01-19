
  const messagesList = document.querySelector('.chat-container');
  const messageForm = document.querySelector('.message-form');
  const messageInput = document.querySelector('.message-input');
  let message_chat=null;
  
  const typingIndicator = document.getElementById('typingIndicator');

  messageForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (message.length === 0) {
      return;
    }

    const messageItem = document.createElement('div');
    message_chat = document.createElement('div');

    message_chat.setAttribute('class', 'message bot');
    message_chat.innerHTML = `
         <div class="avatar">🤖</div>
         <div class="bubble typing-indicator">
             <span></span>
             <span></span>
             <span></span>
         </div>
       `;
    messageItem.setAttribute('class', 'message user');
    messageItem.classList.add('message', 'sent');
    messageItem.innerHTML = `
                    <div class="bubble">
                          ${message}
                    </div>
                    <div class="avatar">🧑</div>
                    `;

    messagesList.appendChild(messageItem);
    messagesList.appendChild(message_chat);

    messageInput.value = '';

  fetch('', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        'message': message
      })
    })
      .then(response => response.json())
      .then(data => {
        const response = data.response;
        const messageItem = document.createElement('div');
        messageItem.setAttribute('class', 'message bot');
        messageItem.classList.add('message', 'received');
        messageItem.innerHTML = `
         <div class="bubble">
                         ${response}
                     </div>
         <div class="avatar">🤖</div>
        `;
         message_chat.remove();
         message_chat = null;
         messagesList.appendChild(messageItem);
         
      });
  });


      function toggleUserMenu() {
          const menu = document.getElementById("userMenu");
          menu.classList.toggle("show");
}

//logout start
const logoutBtn = document.getElementById('logoutBtn');

     logoutBtn.addEventListener('click', () => {

    // opcional: limpar dados locais
     localStorage.clear();
     sessionStorage.clear();

    // redireciona para login
    window.location.replace('/logout');
});
//logout end

const chat = document.getElementById("chat-container");
const scrollBtnWrapper = document.getElementById("scrollBtnWrapper");

function scrollToBottom() {
    chat.scrollTo({
        top: chat.scrollHeight,
        behavior: "smooth"
    });
}

/* Mostrar botão só quando NÃO está no fundo */
chat.addEventListener("scroll", () => {
    const isAtBottom =
        chat.scrollTop + chat.clientHeight >= chat.scrollHeight - 10;

    scrollBtnWrapper.style.display = isAtBottom ? "none" : "flex";
});

/* Ao carregar a página, ir para o fundo */
window.onload = () => {
    scrollToBottom();
};

const input = document.getElementById("messageInput");

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});


// Função para enviar mensagem ao clicar Enter

function sendMessage() {
    const message = input.value.trim();

    if (!message) return;


    if (message.length === 0) {
      return;
    }

    const messageItem = document.createElement('div');
    message_chat = document.createElement('div');

    message_chat.setAttribute('class', 'message bot');
    message_chat.innerHTML = `
         <div class="avatar">🤖</div>
         <div class="bubble typing-indicator">
             <span></span>
             <span></span>
             <span></span>
         </div>
       `;
    messageItem.setAttribute('class', 'message user');
    messageItem.classList.add('message', 'sent');
    messageItem.innerHTML = `
                    <div class="bubble">
                          ${message}
                    </div>
                    <div class="avatar">🧑</div>
                    `;

    messagesList.appendChild(messageItem);
    messagesList.appendChild(message_chat);

    messageInput.value = '';

  fetch('', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        'message': message
      })
    })
      .then(response => response.json())
      .then(data => {
        const response = data.response;
        const messageItem = document.createElement('div');
        messageItem.setAttribute('class', 'message bot');
        messageItem.classList.add('message', 'received');
        messageItem.innerHTML = `
         <div class="bubble">
                         ${response}
                     </div>
         <div class="avatar">🤖</div>
        `;
         message_chat.remove();
         message_chat = null;
         messagesList.appendChild(messageItem);
         
      });

    input.value = "";
}
