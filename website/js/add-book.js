/**
 * Add Book Modal JavaScript
 * Handles the add book functionality for the library
 */

const AddBookManager = {
    modal: null,
    form: null,
    overlay: null,

    init() {
        this.createModal();
        this.bindEvents();
    },

    createModal() {
        // Create modal HTML
        const modalHTML = `
            <div class="modal-overlay" id="addBookOverlay"></div>
            <div class="modal add-book-modal" id="addBookModal">
                <div class="modal-header">
                    <h2 class="modal-title">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                            <line x1="12" y1="8" x2="12" y2="14"></line>
                            <line x1="9" y1="11" x2="15" y2="11"></line>
                        </svg>
                        Thêm Truyện Mới
                    </h2>
                    <button class="modal-close" id="closeAddBookModal" title="Đóng">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                
                <form class="add-book-form" id="addBookForm">
                    <div class="form-section">
                        <h3 class="form-section-title">Thông tin cơ bản</h3>
                        
                        <div class="form-group">
                            <label class="form-label" for="bookTitleEn">
                                Tên truyện (tiếng Anh/gốc) <span class="required">*</span>
                            </label>
                            <input type="text" id="bookTitleEn" name="titleEn" required 
                                   placeholder="Ví dụ: Max Level Priest" class="form-input">
                            <span class="form-hint">Tên gốc của truyện</span>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="bookTitleVi">
                                Tên truyện (tiếng Việt) <span class="required">*</span>
                            </label>
                            <input type="text" id="bookTitleVi" name="titleVi" required 
                                   placeholder="Ví dụ: Linh Mục Cấp Tối Đa" class="form-input">
                            <span class="form-hint">Tên dịch tiếng Việt</span>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="bookGenre">
                                    Thể loại <span class="required">*</span>
                                </label>
                                <select id="bookGenre" name="genre" required class="form-select">
                                    <option value="">Chọn thể loại</option>
                                    <option value="Light Novel">Light Novel</option>
                                    <option value="Web Novel">Web Novel</option>
                                    <option value="Manhwa">Manhwa</option>
                                    <option value="Manga">Manga</option>
                                    <option value="Tiểu thuyết">Tiểu thuyết</option>
                                    <option value="Truyện ngắn">Truyện ngắn</option>
                                    <option value="Khác">Khác</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label" for="bookStatus">
                                    Trạng thái
                                </label>
                                <select id="bookStatus" name="status" class="form-select">
                                    <option value="ongoing">Đang tiến hành</option>
                                    <option value="complete">Hoàn thành</option>
                                    <option value="hiatus">Tạm dừng</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="bookDescription">
                                Mô tả ngắn
                            </label>
                            <textarea id="bookDescription" name="description" rows="3" 
                                      placeholder="Viết mô tả ngắn về truyện..." class="form-textarea"></textarea>
                            <span class="form-hint">Mô tả sẽ hiển thị trên thẻ truyện (tối đa 200 ký tự)</span>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h3 class="form-section-title">Thông tin bổ sung</h3>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="bookAuthor">
                                    Tác giả
                                </label>
                                <input type="text" id="bookAuthor" name="author" 
                                       placeholder="Tên tác giả" class="form-input">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label" for="bookVolumes">
                                    Số Volume
                                </label>
                                <input type="number" id="bookVolumes" name="volumes" 
                                       placeholder="0" min="0" class="form-input">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="bookCoverUrl">
                                URL ảnh bìa (tùy chọn)
                            </label>
                            <input type="url" id="bookCoverUrl" name="coverUrl" 
                                   placeholder="https://example.com/cover.jpg" class="form-input">
                            <span class="form-hint">Để trống nếu chưa có ảnh bìa</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" id="cancelAddBook">
                            Hủy bỏ
                        </button>
                        <button type="submit" class="btn btn-primary" id="submitAddBook">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                            Tạo Truyện
                        </button>
                    </div>
                </form>
                
                <div class="add-book-success" id="addBookSuccess" style="display: none;">
                    <div class="success-icon">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                    <h3 class="success-title">Tạo truyện thành công!</h3>
                    <p class="success-message" id="successMessage"></p>
                    <div class="success-actions">
                        <button class="btn btn-secondary" id="addAnotherBook">Thêm truyện khác</button>
                        <a href="#" class="btn btn-primary" id="goToNewBook">Đi đến truyện</a>
                    </div>
                </div>
            </div>
        `;

        // Append modal to body
        const container = document.createElement('div');
        container.id = 'addBookContainer';
        container.innerHTML = modalHTML;
        document.body.appendChild(container);

        // Store references
        this.modal = document.getElementById('addBookModal');
        this.overlay = document.getElementById('addBookOverlay');
        this.form = document.getElementById('addBookForm');
    },

    bindEvents() {
        // Open modal when clicking add placeholder
        const addPlaceholder = document.getElementById('addBookPlaceholder');
        if (addPlaceholder) {
            addPlaceholder.addEventListener('click', () => this.openModal());
            addPlaceholder.style.cursor = 'pointer';
        }

        // Close modal events
        document.getElementById('closeAddBookModal')?.addEventListener('click', () => this.closeModal());
        document.getElementById('cancelAddBook')?.addEventListener('click', () => this.closeModal());
        this.overlay?.addEventListener('click', () => this.closeModal());

        // Form submission
        this.form?.addEventListener('submit', (e) => this.handleSubmit(e));

        // Add another book
        document.getElementById('addAnotherBook')?.addEventListener('click', () => this.resetForm());

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal?.classList.contains('active')) {
                this.closeModal();
            }
        });

        // Character counter for description
        const descInput = document.getElementById('bookDescription');
        if (descInput) {
            descInput.addEventListener('input', () => {
                const hint = descInput.nextElementSibling;
                const remaining = 200 - descInput.value.length;
                hint.textContent = `Mô tả sẽ hiển thị trên thẻ truyện (còn ${remaining} ký tự)`;
                if (remaining < 0) {
                    hint.style.color = 'var(--accent)';
                } else {
                    hint.style.color = '';
                }
            });
        }
    },

    openModal() {
        this.modal?.classList.add('active');
        this.overlay?.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Focus first input
        setTimeout(() => {
            document.getElementById('bookTitleEn')?.focus();
        }, 100);
    },

    closeModal() {
        this.modal?.classList.remove('active');
        this.overlay?.classList.remove('active');
        document.body.style.overflow = '';
    },

    resetForm() {
        this.form?.reset();
        document.getElementById('addBookSuccess').style.display = 'none';
        this.form.style.display = '';
        document.getElementById('bookTitleEn')?.focus();
    },

    generateSlug(title) {
        return title
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/đ/g, 'd')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .substring(0, 50);
    },

    async handleSubmit(e) {
        e.preventDefault();

        const formData = new FormData(this.form);
        const bookData = {
            titleEn: formData.get('titleEn').trim(),
            titleVi: formData.get('titleVi').trim(),
            genre: formData.get('genre'),
            status: formData.get('status'),
            description: formData.get('description').trim().substring(0, 200),
            author: formData.get('author').trim(),
            volumes: parseInt(formData.get('volumes')) || 0,
            coverUrl: formData.get('coverUrl').trim(),
            slug: this.generateSlug(formData.get('titleEn')),
            createdAt: new Date().toISOString()
        };

        // Validate required fields
        if (!bookData.titleEn || !bookData.titleVi || !bookData.genre) {
            this.showError('Vui lòng điền đầy đủ các trường bắt buộc!');
            return;
        }

        // Show loading state
        const submitBtn = document.getElementById('submitAddBook');
        const originalContent = submitBtn.innerHTML;
        submitBtn.innerHTML = `
            <span class="spinner-small"></span>
            Đang tạo...
        `;
        submitBtn.disabled = true;

        try {
            // Store book data in localStorage for persistence
            this.saveBookToLibrary(bookData);

            // Add book card to the grid
            this.addBookToGrid(bookData);

            // Show success message
            this.showSuccess(bookData);

        } catch (error) {
            console.error('Error creating book:', error);
            this.showError('Có lỗi xảy ra khi tạo truyện. Vui lòng thử lại.');
        } finally {
            submitBtn.innerHTML = originalContent;
            submitBtn.disabled = false;
        }
    },

    saveBookToLibrary(bookData) {
        const books = JSON.parse(localStorage.getItem('library_books') || '[]');

        // Check if slug already exists
        const existingIndex = books.findIndex(b => b.slug === bookData.slug);
        if (existingIndex >= 0) {
            // Generate unique slug
            bookData.slug = `${bookData.slug}-${Date.now()}`;
        }

        books.push(bookData);
        localStorage.setItem('library_books', JSON.stringify(books));
    },

    addBookToGrid(bookData) {
        const grid = document.getElementById('booksList');
        const placeholder = document.getElementById('addBookPlaceholder');

        if (!grid) return;

        const statusClass = bookData.status === 'complete' ? 'status-complete' : 'status-ongoing';
        const statusText = {
            'ongoing': 'Đang tiến hành',
            'complete': 'Hoàn thành',
            'hiatus': 'Tạm dừng'
        }[bookData.status] || 'Đang tiến hành';

        const bookCard = document.createElement('a');
        bookCard.href = `books/${bookData.slug}/index.html`;
        bookCard.className = 'book-card';
        bookCard.setAttribute('data-book-slug', bookData.slug);

        const coverContent = bookData.coverUrl
            ? `<img src="${bookData.coverUrl}" alt="${bookData.titleEn}">`
            : `<div class="book-cover-placeholder">
                 <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                   <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                   <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                 </svg>
               </div>`;

        bookCard.innerHTML = `
            <div class="book-cover">
                ${coverContent}
            </div>
            <div class="book-info">
                <span class="book-genre">${bookData.genre}</span>
                <h3 class="book-title">${bookData.titleEn}</h3>
                <p class="book-title-vi">${bookData.titleVi}</p>
                <div class="book-meta">
                    <span class="book-chapters">0 chương</span>
                    <span class="book-status ${statusClass}">${statusText}</span>
                </div>
                <p class="book-description">${bookData.description || 'Chưa có mô tả.'}</p>
            </div>
        `;

        // Insert before the placeholder
        if (placeholder) {
            grid.insertBefore(bookCard, placeholder);
        } else {
            grid.appendChild(bookCard);
        }

        // Add entrance animation
        bookCard.style.opacity = '0';
        bookCard.style.transform = 'translateY(20px)';
        requestAnimationFrame(() => {
            bookCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            bookCard.style.opacity = '1';
            bookCard.style.transform = 'translateY(0)';
        });
    },

    showSuccess(bookData) {
        this.form.style.display = 'none';
        const successDiv = document.getElementById('addBookSuccess');
        const successMsg = document.getElementById('successMessage');
        const goToBook = document.getElementById('goToNewBook');

        successMsg.textContent = `Truyện "${bookData.titleVi}" đã được thêm vào thư viện.`;
        goToBook.href = `books/${bookData.slug}/index.html`;

        successDiv.style.display = 'block';
    },

    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast toast-error';
        toast.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};

// Load saved books on page load
const LibraryLoader = {
    init() {
        this.loadSavedBooks();
    },

    loadSavedBooks() {
        const books = JSON.parse(localStorage.getItem('library_books') || '[]');
        books.forEach(bookData => {
            AddBookManager.addBookToGrid(bookData);
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    AddBookManager.init();
    LibraryLoader.init();
});
