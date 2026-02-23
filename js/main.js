// DIL Corporation - 리뉴얼: 모바일 메뉴 토글
document.addEventListener('DOMContentLoaded', function () {
  var nav = document.getElementById('nav');
  var toggle = document.getElementById('navToggle');
  if (!nav || !toggle) return;

  toggle.addEventListener('click', function () {
    nav.classList.toggle('is-open');
    toggle.setAttribute('aria-label', nav.classList.contains('is-open') ? '메뉴 닫기' : '메뉴 열기');
  });

  // 메뉴 링크 클릭 시(모바일에서) 메뉴 닫기
  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-label', '메뉴 열기');
    });
  });
});
