<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.0/css/bulma.css">
  <link rel="stylesheet" href="static/style.css">
  <link rel="canonical" href="/">
  <title>fgosccalc</title>
  <script crossorigin async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
  <script crossorigin src="https://unpkg.com/react@16/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@16/umd/react-dom.production.min.js"></script>
  <script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>
</head>
<body>
  <section class="hero is-success">
    <div class="hero-body" style="padding: 2rem 1.5rem">
      <div class="container">
        <p class="title">fgosccalc</p>
        <p class="subtitle">FGOスクショ差分チェッカー</p>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="content">
% if not result:
      % if not sc1_available:
        <p>画像1を正常に解析できませんでした。アップロードしたファイルが正しいか確認してください。</p>
      % end
      % if not sc2_available:
        <p>画像2を正常に解析できませんでした。アップロードしたファイルが正しいか確認してください。</p>
      % end
        <div class="tile is-ancestor">
          <div class="tile is-parent">
            <article class="tile is-child box">
            % if before_im:
              <img class="image" src="data:image/png;base64,{{ before_im }}">
            % end
            </article>
          </div>
          <div class="tile is-parent">
            <article class="tile is-child box">
            % if after_im:
              <img class="image" src="data:image/png;base64,{{ after_im }}">
            % end
            </article>
          </div>
        </div>
% else:
        <h3>解析結果</h3>
        <p>{{ result }}</p>

        <table class="is-narrow">
          <thead>
            <tr>
              <th>ドロップ</th>
              <th>差分</th>
              <th>周回前</th>
              <th>周回後</th>
            </tr>
          </thead>
          % for pair in before_after_pairs:
          <tr>
            <td>{{ pair[0] }}</td>
            <td data-label="差">{{ pair[3] }}</td>
            <td data-label="前">{{ pair[1] }}</td>
            <td data-label="後">{{ pair[2] }}</td>
          </tr>
          % end
        </table>

        <div class="tile is-ancestor">
          <div class="tile is-parent">
            <article class="tile is-child box">
            % if before_im:
              <img class="image" src="data:image/png;base64,{{ before_im }}">
            % end
            </article>
          </div>
          <div class="tile is-parent">
            <article class="tile is-child box">
            % if after_im:
              <img class="image" src="data:image/png;base64,{{ after_im }}">
            % end
            </article>
          </div>
        </div>

        <h3><a href="/items" target="_blank">未知アイテム一覧</a></h3>
        <p>
          解析結果に <code>item000001</code> のような名称不明アイテムが含まれている場合、それは未知のアイテムです。
          上記のリンク先で対応する画像を調べることができます。
        </p>
        <h3>周回報告フォーマット編集</h3>
        <!-- react -->
        <div id="app0"></div>

        <ul class="note">
          <li>礼装、種火、また画像の片方が未ドロップの素材。これらは個数が取得できないため <code>NaN</code> と表記されます。</li>
          <li>恒常フリクエについて、画像からクエスト名が判別できる場合は自動でクエスト名が挿入されます。投稿前に誤りがないか確認をお願いします。</li>
          <li>画像解析の結果は常に誤認識の可能性があります。周回前、周回後の数値が正しく拾えているか必ずチェックしてください。自動判定されたクエスト名についても同様です。</li>
        </ul>

        <p><a href="/">戻る</a></p>

        <hr>
        <p>
          <span class="tag is-link is-light is-medium"><a href="https://github.com/fgosc/" target="_blank">fgosc project</a></span>
        </p>
        <p>
          解析エンジン: <a href="https://github.com/fgosc/fgosccalc" target="_blank">fgosccalc</a>
          developed by <a href="https://twitter.com/fgophi" target="_blank">fgophi</a>
          <br>
          <a href="https://twitter.com/max747_fgo" target="_blank">連絡先</a>
        </p>
      </div><!-- content -->
    </div><!-- container -->
  </section>
  <script>
    var questname = '{{ questname }}';
    var runcount = '000';
    var data = JSON.parse('{{! dropdata }}');
  </script>
  <script src="/static/js/dist/report.js"></script>
% end
</body>
</html>
