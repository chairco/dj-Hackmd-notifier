# dj-Hackmd-notifer

Django + Django-Q 開發，用來建立排程與比對 [Hackmd.io](https://hackmd.io/) 上的網頁文件內容的線上工具。


## 環境設定

建議採用 [Pipenv](https://github.com/kennethreitz/pipenv) 做套件管理，Pipenv 是一個出色的 Python 工具管理套件，類似其他程式語言裡常見的：bundler, composer, npm, cargo, yarn, 等

如果對它還不熟悉，這裡有一篇簡單的 [Pipenv 使用教學](https://chairco.github.io/posts/2017/02/Pipenv%20tutorial.html)。

### pipenv

建立環境:
```
pipenv --python 3.6.3
```

安裝必要套件:
```
pipenv install --dev
```

進入虛擬環境:
```
pipenv shell
```


### py3 內建虛擬環境

```
python3 -m venv env
```

進入虛擬環境:
```
source source env/bin/activate 
```

安裝必要套件:
```
pip install -r requirements.txt
```


## Django 環境設定

使用 python-dotenv 管理環境變數，首先需要在 settings/ 目錄下先建立 `local.env` 檔案。

```
cp dj-Hackmd-notifer/src/src/settings/local_sample.env dj-Hackmd-notifer/src/src/settings/local.env 
```

接著設定環境需要參數:

+ `EMAIL_HOST_USER={}` 發送信件 gmail 帳號。
+ `EMAIL_HOST_PASSWORD={}` 發送信件 gmail 密碼。
+ `DATABASE_URL='postgres://localhost/hackmds'` 預設採用 postgresql 資料庫，可根據需求修改(sqlite3 目前測試會有問題)。
+ `SECRET_KEY={}` Django 需要的 secret key。可到[這邊](https://www.miniwebtool.com/django-secret-key-generator/)取得

因為 Google 目前針對帳號安全開啟二階段認證，因此如果需要透過第三方程式發送 gmail 信件，請先至[後台](https://myaccount.google.com/lesssecureapps)關閉二階段認證並且允許第三方程式存取帳戶。 *注意: 這樣修改可能會有資安危險。*


新增 logs 資料夾, 專案所有產生的 log file 都會存放在此
```
cd src
mkdir -p logs
```


建立資料庫:

注意，目前資料庫預設 `Postgresql` 請先在本機端預設安裝，並且建立對應的 table。安裝完成後再執行 migrate 指令。

```
python manage.py migrate
```

建立 admin 帳號(請注意一定要輸入信箱，因為信件會發送到此):
```
python manage.py createsuperuser
```

啟動伺服器：
```
python manage.py runserver
```

如果可以順利連到 [localhost:8000/admin](http://localhost:8000/admin) 恭喜已經完成一半了。


## 排程設定

先進入 [後台網頁](http://localhost:8000/admin/)，並用剛剛建立的 admin 帳號與密碼登入。

![Imgur](https://i.imgur.com/OpHhXEU.png)


點選 `Scheduled tasks` 旁邊的新增排程。

+ `Name` 隨意輸入，不要太複雜。
+ `Func` 執行任務函式，src 是 Django project 名稱, tasks 是檔案名稱, `hackmd_task` 為函式名稱。
+ `Hook` 任務結束時會印出 stdout 的結果。目前還沒印出具體訊息。
+ `Kwargs` 函式需要的參數, 在這裡只需要 `url`。注意因為比對是以 `url` 作為 key 儲存在 db 因此請以 hackmd.io **發表**的網址，例如: https://hackmd.io/s/ByIn4AYaZ, 一定要帶上 https:// 程式未來可為這部分自動偵測。
+ `Schedule type` 多久運作一次。
+ `Repeats` 設定 -1 代表永遠。
+ `Next Run` 點選現在。

最後按儲存完成。 

![Imgur](https://i.imgur.com/5NXFgC2.png)

![Imgur](https://i.imgur.com/yMSlUX8.png)


最後在開啟一個終端機執行 Django-Q:

```
python manage.py qcluster
```

看到下面資訊就代表運作成功，接著稍等一下就會開始執行排程。

```
21:38:27 [Q] INFO Q Cluster-9144 starting.
21:38:27 [Q] INFO Process-1:1 ready for work at 9146
21:38:27 [Q] INFO Process-1:2 ready for work at 9147
21:38:27 [Q] INFO Process-1:3 ready for work at 9148
21:38:27 [Q] INFO Process-1:4 ready for work at 9149
21:38:27 [Q] INFO Process-1:5 monitoring at 9150
21:38:27 [Q] INFO Process-1 guarding cluster at 9145
21:38:27 [Q] INFO Process-1:6 pushing tasks at 9151
21:38:27 [Q] INFO Q Cluster-9144 running.
```


如果有超過五處的修改就會收到信件如：

![Imgur](https://i.imgur.com/rnDd7Xu.png)

![Imgur](https://i.imgur.com/kXyu18I.png)


### 參考

本專案同時參考 @uranusjr 的 diffhtml [專案](https://github.com/uranusjr/diffhtml)在此感謝。




