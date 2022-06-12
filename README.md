# notion-backup

![example workflow name](https://github.com/jckleiner/notion-backup/workflows/notion-backup-build-run/badge.svg?branch=master)

> *********************************************************
> **Notion changed their API on 27.05.2022:** it is no longer possible to fetch the tokenV2 by sending a login request and that's why the build is not working anymore. 
> I will try to find another way to fetch the token
> *********************************************************

Automatically backup your Notion workspace to Google Drive, Dropbox, Nextcloud or to your local machine.

### Set Credentials

Create a `.env` file with the following properties ([How do I find all these values?](./documentation/setup.md)):

    # Make sure not to use any quotes around these environment variables
    
    # Notion (Required)
    NOTION_SPACE_ID=
    NOTION_EMAIL=
    NOTION_PASSWORD=
    # Options: markdown, html (default is markdown)
    NOTION_EXPORT_TYPE=markdown

    # Google Drive (Optional)
    GOOGLE_DRIVE_ROOT_FOLDER_ID=
    GOOGLE_DRIVE_SERVICE_ACCOUNT=
    # Provide either secret json or the path to the secret file
    GOOGLE_DRIVE_SERVICE_ACCOUNT_SECRET_JSON=
    GOOGLE_DRIVE_SERVICE_ACCOUNT_SECRET_FILE_PATH=

    # Dropbox (Optional)
    DROPBOX_ACCESS_TOKEN=

    # Nextcloud (Optional)
    NEXTCLOUD_EMAIL=
    NEXTCLOUD_PASSWORD=
    NEXTCLOUD_WEBDAV_URL=

### Backup to Cloud With Docker

Once you created your `.env` file, you can run the following command to start your backup:

```bash
docker run \
    --rm=true \
    --env-file=.env \
    jckleiner/notion-backup
```

The downloaded Notion export file will be saved to the `/downloads` folder in the Docker container and the container
will be removed after the backup is done (because of the `--rm=true` flag).

If you want automatic backups in regular intervals, you could either set up a cronjob on your local machine or
[fork this repo](#fork-github-actions) and let GitHub Actions do the job.

### Local Backup With Docker

If you want to keep the downloaded files locally, you could mount the `/downloads` folder from the container somewhere
on your machine:

```bash
docker run \
    --rm=true \
    --env-file=.env \
    -v <backup-dir-absolute-path-on-your-machine>:/downloads \
    jckleiner/notion-backup
```

If you want automatic backups in regular intervals, you could either set up a cronjob on your local machine or 
[fork this repo](#fork-github-actions) and let GitHub Actions do the job.

### Fork (GitHub Actions)

Another way to do automated backups is using GitHub Actions. You can simply:

1. Fork this repository.
2. Create repository secrets: Go to `notion-backup (your forked repo) > Settings > Secrets > Actions` and create all
   the [necessary environment variables](#set-credentials).
3. Go to `notion-backup (your forked repo) > Actions` to see the workflows and make sure the 
   `notion-backup-build-run` workflow is enabled. This is the workflow which will periodically build and run the 
   application.
4. You can adjust when the action will be triggered by editing the `schedule > cron` property in your 
   [notion-backup/.github/workflows/build-run.yml](.github/workflows/build-run.yml)
   workflow file (to convert time values into cron expressions: [crontab.guru](https://crontab.guru/)).

That's it. GitHub Actions will now run your workflow regularly at your defined time interval.

## Local Development

Testing Nextcloud file upload from the command-line:

```
# <user> user name in nextcloud
# <pass> password <user>
# <nextcloud root> root folder of nextcloud ex) https://abc.com/nextcloud
# <path of file to download> Path of nextcloud which you want to download
# <path to save> Path of your system which you want to download to
# If the WebDAV URL ends with a `/`, for instance `https://my.nextcloud.tld/remote.php/dav/files/EMAIL/Documents/`: this
  indicates the uploaded file will be placed in the `Documents` folder.
# If the WebDAV URL **does not end** with a `/`, for
  instance `https://my.nextcloud.tld/remote.php/dav/files/EMAIL/Documents/somefile.txt`: this indicates the uploaded
  file will be named `somefile.txt` and it will be placed in the `Documents` folder. If a file with the same name 
  exists, it will be overwritten.
  
curl --user 'USERNAME':'PASSWORD' --upload-file /path/to/file https://my.nextcloud.tld/remote.php/dav/files/USERNAME/path/to/directory/
```

## Troubleshooting

### Dropbox

If you get the exception: `com.dropbox.core.BadResponseException: Bad JSON: expected object value.`, then try to
re-generate your Dropbox access token and run the application again.
