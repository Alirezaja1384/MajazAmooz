$(document).ready(() => {
    $('[data-toggle="tooltip"]').tooltip();
});
$('.owl-carousel').owlCarousel({
    rtl: true,
    loop: false,
    rewind: true,
    margin: 10,
    nav: true,
    autoplay: true,
    autoplayHoverPause: true,
    // autoHeight: true,
    responsive: {
        0: {
            items: 1
        },
        575: {
            items: 2
        },
        992: {
            items: 3
        },
        1200: {
            items: 4
        }
    }
});
