// static/js/main.js

// ============================================
// FUNÇÕES GLOBAIS
// ============================================

// Abrir modal para criar/editar caso
function abrirModalCaso(id = null) {
    const modal = new bootstrap.Modal(document.getElementById('genericModal'));
    const template = document.getElementById('form-caso-template');
    const modalBody = document.getElementById('modalBody');
    const modalTitle = document.getElementById('modalTitle');
    
    modalBody.innerHTML = template.innerHTML;
    
    if (id) {
        modalTitle.innerText = 'Editar Caso';
        carregarDadosCaso(id);
    } else {
        modalTitle.innerText = 'Novo Caso';
        document.getElementById('formCaso').reset();
        document.getElementById('caso_id').value = '';
    }
    
    // Configurar submit do formulário
    const form = document.getElementById('formCaso');
    form.action = window.casos?.salvarUrl || '/casos/salvar/';
    form.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrftoken }
        });
        if (response.ok) {
            modal.hide();
            location.reload();
        } else {
            alert('Erro ao salvar');
        }
    };
    
    modal.show();
}

// Carregar dados para edição
async function carregarDadosCaso(id) {
    const url = window.casos?.dadosUrl.replace('0', id) || `/casos/${id}/dados/`;
    const response = await fetch(url);
    const data = await response.json();
    
    document.getElementById('caso_id').value = data.id;
    document.querySelector('[name="titulo"]').value = data.titulo;
    document.querySelector('[name="contexto"]').value = data.contexto;
    document.querySelector('[name="tecnologia"]').value = data.tecnologia;
    document.querySelector('[name="descricao"]').value = data.descricao;
    document.querySelector('[name="resultado"]').value = data.resultado;
    document.querySelector('[name="tags"]').value = data.tags;
}

// Excluir caso
async function excluirCaso(id) {
    if (!confirm('Tem certeza que deseja excluir este caso?')) return;
    
    const url = window.casos?.excluirUrl.replace('0', id) || `/casos/excluir/${id}/`;
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken }
    });
    
    if (response.ok) {
        location.reload();
    } else {
        alert('Erro ao excluir');
    }
}

// ============================================
// FUNÇÕES PARA MATERIAIS
// ============================================

function abrirModalMaterial(id = null) {
    // Similar ao abrirModalCaso
    console.log('Abrir modal material', id);
}

function excluirMaterial(id) {
    // Similar ao excluirCaso
    console.log('Excluir material', id);
}

// ============================================
// FUNÇÕES PARA VÍDEOS
// ============================================

function abrirModalVideo(id = null) {
    console.log('Abrir modal video', id);
}

function excluirVideo(id) {
    console.log('Excluir video', id);
}

// ============================================
// FUNÇÕES PARA FERRAMENTAS
// ============================================

function abrirModalFerramenta(id = null) {
    console.log('Abrir modal ferramenta', id);
}

function excluirFerramenta(id) {
    console.log('Excluir ferramenta', id);
}

// ============================================
// FUNÇÕES PARA ADMIN USUÁRIOS
// ============================================

function abrirModalUsuario(email = null) {
    console.log('Abrir modal usuario', email);
}

function excluirUsuario(email) {
    if (!confirm(`Tem certeza que deseja excluir ${email}?`)) return;
    console.log('Excluir usuario', email);
}