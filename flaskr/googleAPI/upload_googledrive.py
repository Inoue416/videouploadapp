from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import os

JSON_FILE = os.environ.get('JSON_FILE')
ID = os.environ.get('ID')

def get_drive():
    gauth = GoogleAuth()
    scope = ["https://www.googleapis.com/auth/drive"]
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(JSON_FILE, scope)
    drive = GoogleDrive(gauth)
    return drive

def check_folder(foldername, drive):
    id = None
    for f in drive.ListFile({'q': '"{}" in parents'.format(ID)}).GetList():
        if f['title'] == foldername:
            id = f['id']
            break

    if id == None: # folderがない場合、作成して再検索
        file = drive.CreateFile({'title': foldername, 'parents': [{'id': ID}], 'mimeType': 'application/vnd.google-apps.folder'}).Upload()
        for f in drive.ListFile({'q': '"{}" in parents'.format(ID)}).GetList():
            if f['title'] == foldername:
                id = f['id']
                break
    return id

def upload_drive(foldername, videopath, videoname):
    drive = get_drive()
    check_folder(foldername, drive)
    f_id = check_folder(foldername, drive)
    f = drive.CreateFile({"title": "{}".format(videoname), 'parents': [{'id': f_id}]})
    f.SetContentFile(videopath)
    f.Upload()
    edit_text(drive, foldername + '.txt', foldername, f_id, videoname)
    return

def edit_text(drive, filename, foldername, folder_id, videoname):
    # ファイルの有無を確認
    id = None
    for f in drive.ListFile({'q': '"{}" in parents'.format(folder_id)}).GetList():
        if f['title'] == filename:
            id = f['id']
            break

    if id == None:
        fw=drive.CreateFile({"title": "{}".format(filename), "parents": [{'id': folder_id}]})
        fw.SetContentString('')
        fw.Upload()
        for f in drive.ListFile({'q': '"{}" in parents'.format(folder_id)}).GetList():
            if f['title'] == filename:
                f.GetContentFile(filename)
                update = f.GetContentString() + 'video/'+ foldername + '/{}'.format(videoname) + '\n'
                f.SetContentString(update)
                f.Upload()
                break
    else:
    # テキストファイルの更新処理
        for f in drive.ListFile({'q': '"{}" in parents'.format(folder_id)}).GetList():
            if f['id'] == id:
                f.GetContentFile(filename)
                update = f.GetContentString() + 'video/' + foldername + '/{}'.format(videoname) + '\n'
                f.SetContentString(update)
                f.Upload()
    return
