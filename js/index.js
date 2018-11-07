//typewriter
var colorPicker = ["#37e5d4", "#00bbeb", "#3089e5", "#8DD7E8"];
var color;
var TxtType = function (el, toRotate, period) {
    this.toRotate = toRotate;
    this.el = el;
    this.loopNum = 0;
    this.period = parseInt(period, 10) || 2000;
    this.txt = '';
    this.tick();
    this.isDeleting = false;
};

TxtType.prototype.tick = function () {
    var i = this.loopNum % this.toRotate.length;
    var fullTxt = this.toRotate[i];
    color = colorPicker[i];

    if (this.isDeleting) {
        this.txt = fullTxt.substring(0, this.txt.length - 1);
    } else {
        this.txt = fullTxt.substring(0, this.txt.length + 1);
    }

    this.el.innerHTML = '<span class="wrap" style="color:' + color + '; border-right-color:' + color + '">' + this.txt + '</span>';

    var that = this;
    var delta = 100;

    if (this.isDeleting) { delta /= 2; }

    if (!this.isDeleting && this.txt === fullTxt) {
        delta = this.period;
        this.isDeleting = true;
    } else if (this.isDeleting && this.txt === '') {
        this.isDeleting = false;
        this.loopNum++;
        delta = 500;
    }

    setTimeout(function () {
        that.tick();
    }, delta);
};


window.onload = function () {
    var elements = document.getElementsByClassName('typewrite');
    for (var i = 0; i < elements.length; i++) {
        var toRotate = elements[i].getAttribute('data-type');
        var period = elements[i].getAttribute('data-period');
        if (toRotate) {
            new TxtType(elements[i], JSON.parse(toRotate), period);
        }
    }
    // INJECT CSS
    var css = document.createElement("style");
    css.type = "text/css";
    css.innerHTML = '.typewrite > .wrap { border-right: 0.08em solid;}';
    document.body.appendChild(css);
};

//about
var nav_parent = $(".about-nav-button");
var about_content = $(".about-content");
var theme = $("#theme-1, #theme-2, #theme-3");

nav_parent.click(function () {
    about_content.removeClass("active");
    var num = $(this).attr("data-num") - 1;
    $(about_content[num]).addClass("active");
});
$(about_content[0]).addClass("active");

theme.click(function () {
    var id = $(this).attr("id");
    $("#theme-content-1, #theme-content-2, #theme-content-3").hide();
    if (id == "theme-1") {
        $("#theme-content-1").slideDown("slow");
    } else if (id == "theme-2") {
        $("#theme-content-2").slideDown("slow");
    } else if (id == "theme-3") {
        $("#theme-content-3").slideDown("slow");
    }
})

//faq
$("li.question").siblings().hide();

$("li.question").click(function () {
    $(this).siblings().slideToggle();

    if ($(this).children().hasClass("rotate")) {
        $(this).children().removeClass("rotate");
        $(this).children().addClass("reverse");
    } else if ($(this).children().hasClass("reverse")) {
        $(this).children().removeClass("reverse");
        $(this).children().addClass("rotate");
    } else {
        $(this).children().addClass("rotate");
    }

});

