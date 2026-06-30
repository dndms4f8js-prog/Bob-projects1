// Markdownリアルタイムプレビュー
document.addEventListener('DOMContentLoaded', function () {
  var descTextarea = document.getElementById('description');
  var descPreview = document.getElementById('description-preview');
  if (descTextarea && descPreview) {
    function updatePreview() {
      var md = descTextarea.value;
      descPreview.innerHTML = md ? marked.parse(md) : '<span class="text-muted small">プレビュー</span>';
    }
    descTextarea.addEventListener('input', updatePreview);
    updatePreview(); // 編集時の初期表示
  }
});

// Markdownツールバー
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.md-toolbar').forEach(function (toolbar) {
    var targetId = toolbar.getAttribute('data-target');
    var textarea = document.getElementById(targetId);
    if (!textarea) return;

    toolbar.querySelectorAll('.md-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var action = btn.getAttribute('data-action');
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var selected = textarea.value.substring(start, end);
        var before = textarea.value.substring(0, start);
        var after = textarea.value.substring(end);

        var inserted = '';
        var cursorOffset = 0;

        if (action === 'bold') {
          if (selected) {
            inserted = '**' + selected + '**';
            cursorOffset = inserted.length;
          } else {
            inserted = '****';
            cursorOffset = 2; // **の内側にカーソルを置く
          }
        } else if (action === 'list') {
          if (selected) {
            // 選択範囲の各行頭に「- 」を付ける
            inserted = selected.split('\n').map(function (line) {
              return '- ' + line;
            }).join('\n');
            cursorOffset = inserted.length;
          } else {
            inserted = '- ';
            cursorOffset = 2;
          }
        }

        textarea.value = before + inserted + after;
        textarea.focus();
        textarea.setSelectionRange(start + cursorOffset, start + cursorOffset);
      });
    });
  });
});
