<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="robots" content="noindex,nofollow,noarchive">
        <link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">
        <link rel="stylesheet" href="static/style.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>FGOスクショ差分チェッカー</title>
        <style type="text/css">
            .image {
                text-align: center;
            }
            .image-caption {
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h2>未知アイテム一覧</h2>
        % if items:
        <div class="row">
        % for k, v in items.items():
            <div class="card fluid">
                <div class="section">
                    <div><img style="height: 7rem;" src="data:image/png;base64,{{ v }}"></div>
                    <p class="image-caption">{{ k }}</p>
                </div>
            </div>
        % end
        </div>
        % end
    </body>
</html>
