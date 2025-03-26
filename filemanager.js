const fileList = document.getElementById("file-list");

let fileSystem = JSON.parse(localStorage.getItem('fileSystem')) || [
    { 
        name: "Chemistry", 
        type: "folder", 
        files: [] 
    },
    { 
        name: "Physics", 
        type: "folder", 
        files: [] 
    },
    { 
        name: "Maths", 
        type: "folder", 
        files: [] 
    }
];

let currentFolder = null;
let itemToDelete = null;

function createNewFolderButton() {
    const newFolderDiv = document.createElement("div");
    newFolderDiv.classList.add("folder", "new-folder");
    newFolderDiv.innerHTML = `
        <img src="https://cdn-icons-png.flaticon.com/128/3767/3767084.png" alt="New Folder">
        <span>+</span>
    `;
    newFolderDiv.onclick = createNewFolder;
    return newFolderDiv;
}

function createNewFolder(e) {
    e.stopPropagation(); // Prevent event bubbling
    const folderName = prompt("Enter folder name:");
    if (folderName && folderName.trim()) {
        const newFolder = {
            name: folderName.trim(),
            type: "folder",
            files: []
        };
        fileSystem.push(newFolder);
        updateFileSystemStorage();
        renderFiles();
    }
}

function getFileIcon(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': 'https://cdn-icons-png.flaticon.com/128/337/337946.png',
        'doc': 'https://cdn-icons-png.flaticon.com/128/4725/4725970.png',
        'docx': 'https://cdn-icons-png.flaticon.com/128/4725/4725970.png',
        'txt': 'https://cdn-icons-png.flaticon.com/128/3767/3767084.png',
        'jpg': 'https://cdn-icons-png.flaticon.com/128/337/337940.png',
        'jpeg': 'https://cdn-icons-png.flaticon.com/128/337/337940.png',
        'png': 'https://cdn-icons-png.flaticon.com/128/337/337940.png'
    };
    return iconMap[extension] || 'https://cdn-icons-png.flaticon.com/128/337/337946.png';
}

function handleFileUpload(folderIndex) {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.multiple = true;
    
    fileInput.onchange = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (event) => {
                fileSystem[folderIndex].files.push({
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    data: event.target.result
                });
                renderFiles();
            };
            reader.readAsDataURL(file);
        });
    };
    
    fileInput.click();
}

function viewFile(file) {
    const viewer = document.getElementById('fileViewer');
    const title = document.getElementById('fileViewerTitle');
    const content = document.getElementById('fileViewerContent');
    
    title.textContent = file.name;
    
    if (file.type.startsWith('image/')) {
        content.innerHTML = `<img src="${file.data}" alt="${file.name}">`;
    } else if (file.type === 'application/pdf') {
        content.innerHTML = `<embed src="${file.data}" type="application/pdf" width="100%" height="600px">`;
    } else {
        // For text files and other types
        try {
            const textContent = file.data.includes('base64') ? 
                atob(file.data.split(',')[1]) : file.data;
            content.innerHTML = `<pre>${textContent}</pre>`;
        } catch (e) {
            content.innerHTML = `<pre>${file.data}</pre>`;
        }
    }
    
    viewer.style.display = 'block';
}

function renderFiles() {
    fileList.innerHTML = "";

    if (currentFolder === null) {
        // Add the "Add Folder" button
        const addFolderBtn = document.createElement("div");
        addFolderBtn.className = "folder";
        addFolderBtn.style.cursor = "pointer";
        addFolderBtn.innerHTML = `
            <div class="file-actions"></div>
            <img src="https://cdn-icons-png.flaticon.com/128/3767/3767084.png" alt="New Folder">
            <span>+ New Folder</span>
        `;
        addFolderBtn.onclick = createNewFolder;
        fileList.appendChild(addFolderBtn);

        // Render folders
        fileSystem.forEach((item, index) => {
            const folderDiv = document.createElement("div");
            folderDiv.className = "folder";
            folderDiv.innerHTML = `
                <div class="file-actions">
                    <button class="action-btn" onclick="event.stopPropagation(); showDeleteConfirmation('folder', ${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <img src="https://cdn-icons-png.flaticon.com/128/3767/3767084.png" alt="Folder">
                <span>${item.name}</span>
                <span class="file-count">${item.files.length} files</span>
            `;
            folderDiv.onclick = () => openFolder(index);
            fileList.appendChild(folderDiv);
        });
    } else {
        // Create header container for back button and title
        const headerDiv = document.createElement("div");
        headerDiv.style.width = "100%";
        headerDiv.style.display = "flex";
        headerDiv.style.alignItems = "center";
        headerDiv.style.marginBottom = "20px";
        
        // Back button
        const backButton = document.createElement("div");
        backButton.className = "folder";
        backButton.style.marginRight = "20px";
        backButton.innerHTML = `
            <img src="https://cdn-icons-png.flaticon.com/128/3767/3767084.png" alt="Back">
            <span>← Back</span>
        `;
        backButton.onclick = goBack;
        headerDiv.appendChild(backButton);
        
        fileList.appendChild(headerDiv);

        // Add centered upload section when folder is empty
        if (fileSystem[currentFolder].files.length === 0) {
            const uploadSection = document.createElement("div");
            uploadSection.className = "upload-section";
            uploadSection.innerHTML = `
                <div class="upload-container">
                    <i class="fas fa-cloud-upload-alt"></i>
                    <h3>Drop files here or click to upload</h3>
                    <p>Supported files: PDF, DOC, TXT, Images</p>
                </div>
            `;
            uploadSection.onclick = () => handleFileUpload(currentFolder);
            fileList.appendChild(uploadSection);
        } else {
            // Render existing files
            fileSystem[currentFolder].files.forEach((file, fileIndex) => {
                const fileDiv = document.createElement("div");
                fileDiv.className = "file";
                fileDiv.innerHTML = `
                    <div class="file-actions">
                        <button class="action-btn" onclick="event.stopPropagation(); showDeleteConfirmation('file', ${fileIndex})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <img src="${getFileIcon(file.name)}" alt="File">
                    <span>${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                `;
                fileDiv.onclick = () => viewFile(file);
                fileList.appendChild(fileDiv);
            });

            // Add upload button at the end
            const uploadButton = document.createElement("div");
            uploadButton.className = "folder upload-btn-container";
            uploadButton.innerHTML = `
                <i class="fas fa-plus"></i>
                <span>Upload More Files</span>
            `;
            uploadButton.onclick = () => handleFileUpload(currentFolder);
            fileList.appendChild(uploadButton);
        }
    }
}

function formatFileSize(bytes) {
    if (!bytes) return '';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

function openFolder(index) {
    currentFolder = index;
    renderFiles();
}

function goBack() {
    currentFolder = null;
    renderFiles();
}

function updateFileSystemStorage() {
    localStorage.setItem('fileSystem', JSON.stringify(fileSystem));
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    renderFiles();

    // Add event listeners for modals
    document.getElementById('deleteModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            cancelDelete();
        }
    });

    document.getElementById('fileViewer')?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeFileViewer();
        }
    });
});