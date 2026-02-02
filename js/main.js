// DIL Corporation - 스크롤, 숫자 애니메이션, 헤더, 등장 애니메이션, 언어 전환
document.addEventListener('DOMContentLoaded', function () {
  // 언어 전환 (한국어 / 영어)
  var body = document.body;
  var langToggle = document.querySelector('.lang-toggle');
  var titles = {
    ko: 'DIL Corporation | 데이터 기반으로 이커머스를 자동화하다',
    en: 'DIL Corporation | Data-driven e-commerce automation'
  };

  function setLang(lang) {
    body.setAttribute('data-lang', lang);
    document.documentElement.lang = lang === 'ko' ? 'ko' : 'en';
    document.title = titles[lang] || titles.ko;

    document.querySelectorAll('[data-ko][data-en]').forEach(function (el) {
      var raw = el.getAttribute('data-' + lang) || '';
      var decoded = raw.replace(/&lt;br\s*\/?&gt;/gi, '<br>').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
      if (raw.indexOf('<') !== -1 || raw.indexOf('&lt;') !== -1) {
        try { el.innerHTML = decoded; } catch (e) { el.textContent = raw; }
      } else {
        el.textContent = raw;
      }
    });

    if (langToggle) {
      var koEl = langToggle.querySelector('.lang-ko');
      var enEl = langToggle.querySelector('.lang-en');
      if (koEl) koEl.setAttribute('data-active', lang === 'ko' ? 'true' : 'false');
      if (enEl) enEl.setAttribute('data-active', lang === 'en' ? 'true' : 'false');
    }
  }

  if (langToggle) {
    langToggle.addEventListener('click', function (e) {
      e.preventDefault();
      var t = e.target;
      if (t.classList.contains('lang-ko')) setLang('ko');
      else if (t.classList.contains('lang-en')) setLang('en');
    });
    var initial = body.getAttribute('data-lang') || 'ko';
    setLang(initial);
  }

  // 네비게이션 스무스 스크롤
  document.querySelectorAll('.nav a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id === '#') return;
      e.preventDefault();
      var el = document.querySelector(id);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // 스크롤 등장 애니메이션: .anim-on-scroll 요소에 .is-visible 추가
  var animElements = document.querySelectorAll('.anim-on-scroll');
  var scrollObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          scrollObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );
  animElements.forEach(function (el) {
    scrollObserver.observe(el);
  });

  // 히어로 통계 숫자 카운트업
  var statValues = document.querySelectorAll('.stat-value[data-target]');
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = el.getAttribute('data-target');
        var num = parseInt(target, 10);
        if (isNaN(num)) return;
        var duration = 1500;
        var start = 0;
        var startTime = null;
        function step(timestamp) {
          if (!startTime) startTime = timestamp;
          var progress = Math.min((timestamp - startTime) / duration, 1);
          var easeOut = 1 - Math.pow(1 - progress, 2);
          el.textContent = Math.floor(start + (num - start) * easeOut);
          if (progress < 1) requestAnimationFrame(step);
          else el.textContent = num;
        }
        requestAnimationFrame(step);
        observer.unobserve(el);
      });
    },
    { threshold: 0.5, rootMargin: '0px' }
  );
  statValues.forEach(function (el) {
    observer.observe(el);
  });

  // 헤더 배경은 CSS와 동일하게 유지 (스크롤 시 변경 없음)
});
