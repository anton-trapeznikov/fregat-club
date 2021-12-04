(function fregatNamespace(){
    let resizeHandlers = [];
    let onReadyHandlers = [];
    let page = null;

    window.storage = JSON.parse(document.getElementById('backendData').textContent);
    window.methods = {
        ui: {}
    }

    function onReady(payload) {
        if (document.readyState != 'loading'){
            payload();
        } else {
            document.addEventListener('DOMContentLoaded', payload);
        }
    }


    function onReize() {
        Array.prototype.forEach.call(resizeHandlers, function(f, i){
            f();
        });
    }

    window.addEventListener("resize", resizeThrottler, false);
    let resizeTimeout;
    function resizeThrottler() {
        if (!resizeTimeout) {
            resizeTimeout = setTimeout(function() {
                resizeTimeout = null;
                onReize();
            }, 300);
        }
    }

    onReady(function(){
        Array.prototype.forEach.call(onReadyHandlers, function(f, i){
            f();
        });

        onReize();
    });


    (function mapNamespace(){
        onReadyHandlers.push(function(){
            if (window.storage.geo.latitude && window.storage.geo.longitude) {
                const latitude = window.storage.geo.latitude;
                const longitude = window.storage.geo.longitude;

                ymaps.ready(init);

                function init() {
                    let map = new ymaps.Map("footer__map", {
                            center: [latitude, longitude],
                            zoom: 15
                        }, {
                            searchControlProvider: 'yandex#search',
                        }),

                        mapPoint = new ymaps.GeoObject({
                            geometry: {
                                type: "Point",
                                coordinates: [latitude, longitude]
                            },
                            properties: {
                                iconContent: 'Клуб Фрегат',
                                hintContent: window.storage.contacts.address
                            }
                        }, {
                            preset: 'islands#blackStretchyIcon',
                            draggable: false
                        });

                    map.behaviors.disable('scrollZoom');
                    map.geoObjects.add(mapPoint);
                }


            }
        });
    })();


    (function mobileMenuNamespace(){
        [].forEach.call(document.querySelectorAll('.mobile-menu__expander'), function(e){
            e.addEventListener('click', function(e) {
                const parent = event.target.closest('.mobile-menu__item');
                parent.classList.toggle('mobile-menu__item_expanded');
            }, false)
        });

        let mobileMenuExtrasWasInit = false;
        let mobileMenuButton = document.getElementById('main-menu__mobile-menu-button');

        mobileMenuButton.addEventListener('click', function(e) {
            if (!window.storage.topMenu.mobileMenuExpandingNow) {
                window.storage.topMenu.mobileMenuExpandingNow = true;

                page = page || document.getElementById('page');
                page.classList.toggle('page_with-mobile-menu');

                window.storage.topMenu.mobileMenuExpandingNow = false;

                if (!mobileMenuExtrasWasInit) {
                    mobileMenuExtrasWasInit = true;
                    document.getElementById('mobile-menu__overlay').addEventListener('click', function(e) {
                        sendClickEvent(mobileMenuButton);
                    }, false)

                    document.getElementById('mobile-menu__close').addEventListener('click', function(e) {
                        sendClickEvent(mobileMenuButton);
                    }, false)
                }
            }

        }, false)
    })();


    (function mainMenuNamespace(){
        [].forEach.call(document.querySelectorAll('.main-menu__submenu-expander'), function(e){
            e.addEventListener('click', function(e) {
                const parent = event.target.closest('.main-menu__submenu-item');
                parent.classList.toggle('main-menu__submenu-item_expanded');
            }, false)
        });

        onReadyHandlers.push(function(){
            window.storage.topMenu.container = document.getElementById('main-menu__navigation');
            const items = window.storage.topMenu['container'].querySelectorAll('.main-menu__item');
            window.storage.topMenu.items = items.length > 0 && nodeListToArray(items) || [];
            window.storage.topMenu.items.reverse();
        });

        window.addEventListener('resize', function() {
            if (!window.storage.topMenu.resizeIsInProgressNow) {
                window.storage.topMenu.resizeIsInProgressNow = true;
                window.storage.topMenu.container.classList.add('main-menu__navigation_strict-width')
            }
        });

        resizeHandlers.push(function(){
            const container = window.storage.topMenu.container;
            let containerWidth = getElementWidth(container) - getLeftPadding(container) - getRightPadding(container);

            if (containerWidth && containerWidth > 0) {
                const items = window.storage.topMenu.items;

                if (!window.storage.topMenu.widthsWereСalculated) {
                    window.storage.topMenu.itemWidths = 0;

                    Array.prototype.forEach.call(items, function(item, i){
                        let width = Math.ceil(getElementWidth(item) + getLeftMargin(item) + getRightMargin(item));
                        item.dataset.width = width;
                        if (i > 0) {
                            window.storage.topMenu.itemWidths += width;
                        } else {
                            window.storage.topMenu.itemExtaWidth = width;
                            window.storage.topMenu.extraItem = item;
                        }
                    });
                    if (window.storage.topMenu.itemWidths > 0)
                        window.storage.topMenu.widthsWereСalculated = true;
                }

                if (containerWidth >= window.storage.topMenu.itemWidths) {
                    Array.prototype.forEach.call(items, function(item, i){
                        if (i > 0) {
                            item.classList.remove('main-menu__item_hidden');
                        } else {
                            item.classList.add('main-menu__item_hidden');
                        }
                    });
                } else {
                    let inMainMenu = [];
                    let diff = window.storage.topMenu.itemWidths - (containerWidth - window.storage.topMenu.itemExtaWidth);

                    Array.prototype.forEach.call(items, function(item, i){
                        if (diff > 0) {
                            if (i == 0) {
                                item.classList.remove('main-menu__item_hidden');
                            } else {
                                diff -= parseInt(item.dataset.width);
                                item.classList.add('main-menu__item_hidden');
                            }
                        } else {
                            item.classList.remove('main-menu__item_hidden');
                            inMainMenu.push(item.dataset.id);
                        }
                    });
                    const submenuItems = window.storage.topMenu.extraItem.querySelectorAll('.main-menu__submenu-item');
                    Array.prototype.forEach.call(submenuItems, function(submenuItem, i){
                        if (inMainMenu.includes(submenuItem.dataset.id)) {
                            submenuItem.classList.add('main-menu__submenu-item_hidden');
                        } else {
                            submenuItem.classList.remove('main-menu__submenu-item_hidden');
                        }
                    });
                }
            }

            container.classList.remove('main-menu__navigation_strict-width');
            window.storage.topMenu.resizeIsInProgressNow = false;
        });
    })();

    (function galleryNamespace(){
        let kbHandlersWasAdded = false;

        onReadyHandlers.push(function(){
            window.methods.ui.openGallery = function(mediaId, templateId) {
                page = page || document.getElementById('page');
                page.classList.add('page_with-gallery');

                const template = document.getElementById(templateId).content.cloneNode(true);
                const container = document.getElementById('page');

                const thumbnails = template.querySelectorAll('.gallery__thumbnail');
                Array.prototype.forEach.call(thumbnails, function(el, i){
                    el.addEventListener('click', function(event){
                        if (!event.target.classList.contains('gallery__thumbnail_active')) {
                            const whois = event.target.dataset.whois;
                            const src = event.target.dataset.src;
                            const parent = event.target.closest('.gallery');

                            let mediaContainer = parent.querySelector('.gallery__media');
                            const caption = parent.querySelector('.gallery__note_caption');
                            const text = parent.querySelector('.gallery__note_text');

                            mediaContainer.classList.add('gallery__media_hidden');
                            caption.classList.add('gallery__note_hidden');
                            text.classList.add('gallery__note_hidden');

                            setTimeout(() => {
                                while(mediaContainer.firstChild) {
                                    mediaContainer.removeChild(mediaContainer.firstChild);
                                }

                                if (event.target.dataset.caption.length > 0) {
                                    caption.querySelector('.gallery__note-inner').textContent = event.target.dataset.caption;
                                }

                                if (event.target.dataset.text.length > 0){
                                    text.querySelector('.gallery__note-inner').textContent = event.target.dataset.text;
                                }

                                let mediaElementTemplateId = whois == 'video' && 'gallery-video-template' || 'gallery-photo-template';
                                let mediaElement = document.getElementById(mediaElementTemplateId).content.cloneNode(true);

                                if (whois == 'video') {
                                    mediaElement.querySelector('.gallery__video').setAttribute('src', 'https://www.youtube.com/embed/' + src);
                                } else {
                                    mediaElement.querySelector('.gallery__image').setAttribute('src', src);
                                }

                                mediaContainer.appendChild(mediaElement);

                                setTimeout(() => {
                                    mediaContainer.classList.remove('gallery__media_hidden');
                                    if (event.target.dataset.caption.length > 0) caption.classList.remove('gallery__note_hidden');
                                    if (event.target.dataset.text.length > 0) text.classList.remove('gallery__note_hidden');
                                }, 200)
                            }, 200);

                            const oldActiveThumbnail = parent.querySelector('.gallery__thumbnail_active');
                            if (oldActiveThumbnail) oldActiveThumbnail.classList.remove('gallery__thumbnail_active');
                            event.target.classList.add('gallery__thumbnail_active');
                        }
                    }, false);

                    if (el.dataset.id === mediaId) {
                        el.click();
                    }
                });

                const navButtons = template.querySelectorAll('.gallery__nav-button');
                Array.prototype.forEach.call(navButtons, function(el, i){
                    el.addEventListener('click', function(event) {
                        const thumbnails = document.querySelectorAll('.gallery__thumbnail');
                        let newIndex = null;
                        const inc = parseInt(event.target.dataset.inc);
                        const lastIndex = thumbnails.length - 1;

                        for (let index = 0; index <= lastIndex; index++) {
                            const thumb = thumbnails[index];

                            if (thumb.classList.contains('gallery__thumbnail_active')) {
                                newIndex = index + inc;
                                if (newIndex < 0) newIndex = lastIndex;
                                if (newIndex > lastIndex) newIndex = 0;
                            }
                        }

                        thumbnails[newIndex].click();
                    }, false);
                });

                const closeBaloonButtons = template.querySelectorAll('.gallery__close-note-button');
                Array.prototype.forEach.call(closeBaloonButtons, function(el, i){
                    el.addEventListener('click', function(event) {
                        const parent = event.target.closest('.gallery__note');
                        parent.classList.add('gallery__note_hidden');
                    }, false);
                });

                template.querySelector('.gallery__close').addEventListener('click', function(event){
                    let gallery = event.target.closest('.gallery');
                    gallery.parentNode.removeChild(gallery);
                    page.classList.remove('page_with-gallery');
                }, false);

                container.appendChild(template);

                if (!kbHandlersWasAdded) {
                    kbHandlersWasAdded = true;

                    document.addEventListener('backbutton', function(event) {
                        let closeBtn = document.querySelector('.gallery__close');
                        if (closeBtn) closeBtn.click();
                    })

                    document.addEventListener('keyup', function(event) {
                        let closeWindow = false;
                        if (event.key == 'Escape' || event.keyCode == 8) {
                            let closeBtn = document.querySelector('.gallery__close');
                            if (closeBtn) closeBtn.click();
                        } else if (event.keyCode == 39 || event.keyCode == 40) {
                            let nextBtn = document.querySelector('.gallery__nav-button_next');
                            if (nextBtn) nextBtn.click();
                        } else if (event.keyCode == 38 || event.keyCode == 37) {
                            let prevBtn = document.querySelector('.gallery__nav-button_prev');
                            if (prevBtn) prevBtn.click();
                        }
                    })
                }
            };

            const thumbnails = document.querySelectorAll('.article__media');
            Array.prototype.forEach.call(thumbnails, function(el, i){
                el.addEventListener('click', function() {
                    event.preventDefault();
                    event.stopPropagation();
                    window.methods.ui.openGallery(event.target.dataset.id, 'gallery-template');
                }, false);
            });
        });
    })();


    (function yandexReviewsNamespace(){
        onReadyHandlers.push(function(){
            const container = document.getElementById('yandex-reviews-container');
            console.log('---')
            console.log(container)
            if (container) {
                console.log('!!')
                const template = document.getElementById('yandex-reviews').content.cloneNode(true);
                container.appendChild(template);
            }
        });
    })();


})();



