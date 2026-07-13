from controller import YandexDisk

yandex_disk = YandexDisk()

yandex_disk.overwrite_existing_file(
    local_file_path="/home/lenovo/github-repo/Sevise-files-sync/src",
    file_name="test_file_to_send.txt"
)
