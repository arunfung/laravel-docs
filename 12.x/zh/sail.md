
# Laravel Sail

-   [介绍](#introduction)
-   [安装与设置](#installation)
    -   [将 Sail 安装到现有应用](#installing-sail-into-existing-applications)
    -   [重建 Sail 镜像](#rebuilding-sail-images)
    -   [配置 Shell 别名](#configuring-a-shell-alias)
-   [启动与停止 Sail](#starting-and-stopping-sail)
-   [执行命令](#executing-sail-commands)
    -   [执行 PHP 命令](#executing-php-commands)
    -   [执行 Composer 命令](#executing-composer-commands)
    -   [执行 Artisan 命令](#executing-artisan-commands)
    -   [执行 Node / NPM 命令](#executing-node-npm-commands)
-   [数据库交互](#interacting-with-sail-databases)
    -   [MySQL](#mysql)
    -   [MongoDB](#mongodb)
    -   [Redis](#redis)
    -   [Valkey](#valkey)
    -   [Meilisearch](#meilisearch)
    -   [Typesense](#typesense)
-   [文件存储](#file-storage)
-   [运行测试](#running-tests)
    -   [Laravel Dusk](#laravel-dusk)
-   [预览邮件](#previewing-emails)
-   [容器 CLI](#sail-container-cli)
-   [PHP 版本](#sail-php-versions)
-   [Node 版本](#sail-node-versions)
-   [共享你的站点](#sharing-your-site)
-   [使用 Xdebug 调试](#debugging-with-xdebug)
    -   [Xdebug CLI 使用](#xdebug-cli-usage)
    -   [Xdebug 浏览器使用](#xdebug-browser-usage)
-   [自定义配置](#sail-customization)

## 介绍

[Laravel Sail](https://github.com/laravel/sail) 是一个轻量级命令行工具，用于操作 Laravel 默认的 Docker 开发环境。Sail 提供了一个很好的起点，可以在不需要 Docker 经验的情况下使用 PHP、MySQL 和 Redis 构建 Laravel 应用程序。

Sail 的核心是项目根目录下的 `docker-compose.yml` 文件和 `sail` 脚本。`sail` 脚本提供了 CLI 接口，方便与 `docker-compose.yml` 文件中定义的 Docker 容器进行交互。

Laravel Sail 支持 macOS、Linux，以及 Windows（通过 [WSL2](https://docs.microsoft.com/en-us/windows/wsl/about)）。

## 安装与设置

Laravel Sail 会在所有新的 Laravel 应用中自动安装，因此你可以立即开始使用。



### 在现有应用中安装 Sail

如果你希望在现有的 Laravel 应用中使用 Sail，可以通过 Composer 包管理器简单地安装 Sail。当然，这些步骤假设你当前的本地开发环境允许你安装 Composer 依赖：

```shell
composer require laravel/sail --dev
```

安装 Sail 之后，你可以运行 `sail:install` Artisan 命令。此命令会将 Sail 的 `docker-compose.yml` 文件发布到应用根目录，并修改你的 `.env` 文件，添加连接 Docker 服务所需的环境变量：

```shell
php artisan sail:install
```

最后，你可以启动 Sail。要继续学习如何使用 Sail，请继续阅读本文档的剩余内容：

```shell
./vendor/bin/sail up
```

> [!警告]
> 如果你在 Linux 上使用 Docker Desktop，应使用 `default` Docker 上下文，执行以下命令：`docker context use default`。

#### 添加额外服务

如果你希望在现有的 Sail 安装中添加额外服务，可以运行 `sail:add` Artisan 命令：

```shell
php artisan sail:add
```

#### 使用 Devcontainers

如果你希望在 [Devcontainer](https://code.visualstudio.com/docs/remote/containers) 中开发，可以在 `sail:install` 命令中提供 `--devcontainer` 选项。该选项会指示 `sail:install` 命令将默认的 `.devcontainer/devcontainer.json` 文件发布到应用根目录：

```shell
php artisan sail:install --devcontainer
```


### 重建 Sail 镜像

有时你可能希望完全重建 Sail 镜像，以确保镜像中的所有软件包和程序都是最新的。你可以使用 `build` 命令来完成此操作：

```shell
docker compose down -v

sail build --no-cache

sail up
```

### 配置 Shell 别名

默认情况下，Sail 命令是通过随新 Laravel 应用包含的 `vendor/bin/sail` 脚本调用的：

```shell
./vendor/bin/sail up
```

然而，为了避免每次执行 Sail 命令都输入 `vendor/bin/sail`，你可以配置一个 shell 别名，使得执行 Sail 命令更加方便：

```shell
alias sail='sh $([ -f sail ] && echo sail || echo vendor/bin/sail)'
```

为了确保这个别名始终可用，你可以将其添加到你主目录下的 shell 配置文件中，例如 `~/.zshrc` 或 `~/.bashrc`，然后重启你的 shell。

配置别名后，你只需输入 `sail` 就可以执行 Sail 命令。本文档剩余的示例都假设你已经配置了该别名：

```shell
sail up
```

## 启动与停止 Sail

Laravel Sail 的 `docker-compose.yml` 文件定义了多个 Docker 容器，它们协同工作以帮助你构建 Laravel 应用。其中，`laravel.test` 容器是主要的应用容器，用于提供应用服务。

在启动 Sail 之前，请确保本地计算机上没有其他 Web 服务器或数据库在运行。要启动应用的 `docker-compose.yml` 文件中定义的所有 Docker 容器，可以执行 `up` 命令：

```shell
sail up
```



要在后台启动所有 Docker 容器，你可以使用“分离模式（detached mode）”启动 Sail：

```shell
sail up -d
```

一旦应用容器启动，你可以在浏览器中访问项目：[http://localhost。](http://localhost%E3%80%82)

要停止所有容器，你可以直接按 **Control + C** 停止容器的执行。或者，如果容器在后台运行，可以使用 `stop` 命令：

```shell
sail stop
```

## 执行命令

使用 Laravel Sail 时，你的应用是在 Docker 容器中运行的，与本地计算机隔离。然而，Sail 提供了一种方便的方式来对应用执行各种命令，例如任意 PHP 命令、Artisan 命令、Composer 命令以及 Node / NPM 命令。

**在阅读 Laravel 文档时，你经常会看到没有提及 Sail 的 Composer、Artisan 或 Node / NPM 命令。** 这些示例假设这些工具已安装在你的本地计算机上。如果你使用 Sail 作为本地 Laravel 开发环境，则应使用 Sail 来执行这些命令：

```shell
# 在本地运行 Artisan 命令...
php artisan queue:work

# 在 Laravel Sail 容器中运行 Artisan 命令...
sail artisan queue:work
```

### 执行 PHP 命令

PHP 命令可以通过 `php` 命令执行。这些命令将使用为你的应用配置的 PHP 版本运行。要了解 Laravel Sail 可用的 PHP 版本，请参考 [PHP 版本文档](#sail-php-versions)：

```shell
sail php --version

sail php script.php
```



### 执行 Composer 命令

Composer 命令可以通过 `composer` 执行。Laravel Sail 的应用容器中自带 Composer 安装：

```shell
sail composer require laravel/sanctum
```

### 执行 Artisan 命令

Laravel 的 Artisan 命令可以通过 `artisan` 执行：

```shell
sail artisan queue:work
```

### 执行 Node / NPM 命令

Node 命令可以通过 `node` 执行，NPM 命令可以通过 `npm` 执行：

```shell
sail node --version

sail npm run dev
```

如果你愿意，也可以使用 Yarn 替代 NPM：

```shell
sail yarn
```

## 与数据库交互

### MySQL

如你所见，应用的 `docker-compose.yml` 文件中包含 MySQL 容器条目。该容器使用 [Docker 卷](https://docs.docker.com/storage/volumes/) 来确保数据库中的数据在停止和重启容器后仍然保留。

此外，MySQL 容器首次启动时会为你创建两个数据库。第一个数据库的名称来源于 `.env` 文件中的 `DB_DATABASE` 环境变量，用于本地开发。第二个是专门的测试数据库，名为 `testing`，确保测试不会影响开发数据。

启动容器后，你可以通过将应用的 `.env` 文件中的 `DB_HOST` 环境变量设置为 `mysql` 来连接应用中的 MySQL 实例。

如果你希望从本地机器连接 MySQL 数据库，可以使用图形化数据库管理工具，例如 [TablePlus](https://tableplus.com)。默认情况下，MySQL 数据库可通过 `localhost` 的 3306 端口访问，访问凭证对应 `.env` 文件中的 `DB_USERNAME` 和 `DB_PASSWORD`。或者，你也可以使用 `root` 用户连接，其密码同样使用 `.env` 文件中的 `DB_PASSWORD`。



### MongoDB

如果你在安装 Sail 时选择了安装 [MongoDB](https://www.mongodb.com/) 服务，那么你的应用程序的 `docker-compose.yml` 文件中会包含一个 [MongoDB Atlas Local](https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-local-cloud/) 容器的配置。该容器提供带有 Atlas 功能（如 [搜索索引](https://www.mongodb.com/docs/atlas/atlas-search/)）的 MongoDB 文档数据库。
该容器使用了一个 [Docker 卷（volume）](https://docs.docker.com/storage/volumes/)，以确保数据库中存储的数据在停止或重启容器时仍能被持久保存。

当你启动容器后，可以通过在应用程序的 `.env` 文件中设置 `MONGODB_URI` 环境变量为 `mongodb://mongodb:27017` 来连接到 MongoDB 实例。默认情况下，认证（Authentication）是禁用的，但你可以在启动 `mongodb` 容器之前设置 `MONGODB_USERNAME` 和 `MONGODB_PASSWORD` 环境变量来启用认证。然后在连接字符串中加入这些凭据：

```ini
MONGODB_USERNAME=user
MONGODB_PASSWORD=laravel
MONGODB_URI=mongodb://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@mongodb:27017
```

为了让你的应用程序与 MongoDB 无缝集成，你可以安装 [MongoDB 官方维护的 Laravel 驱动包](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/)。

如果你想从本地机器连接到应用程序中的 MongoDB 数据库，可以使用图形化界面工具 [Compass](https://www.mongodb.com/products/tools/compass)。默认情况下，MongoDB 数据库可通过 `localhost` 的 `27017` 端口访问。

### Redis

你的应用程序的 `docker-compose.yml` 文件中同样包含了一个 [Redis](https://redis.io) 容器的配置。
该容器同样使用了一个 [Docker 卷（volume）](https://docs.docker.com/storage/volumes/)，以确保 Redis 实例中的数据在停止或重启容器时依然被持久保存。

当你启动容器后，可以通过在应用程序的 `.env` 文件中设置 `REDIS_HOST` 环境变量为 `redis` 来连接到 Redis 实例。



要从本地计算机连接到应用程序的 Redis 数据库，可以使用图形化数据库管理工具，例如 [TablePlus](https://tableplus.com)。默认情况下，Redis 数据库可通过 `localhost` 的 6379 端口访问。

### Valkey

如果在安装 Sail 时选择安装 Valkey 服务，应用程序的 `docker-compose.yml` 文件中将包含一个 [Valkey](https://valkey.io/) 的配置项。该容器使用 [Docker 卷（Docker volume）](https://docs.docker.com/storage/volumes/)，因此即使停止或重新启动容器，存储在 Valkey 实例中的数据也会被持久化。
你可以在应用程序中通过在 `.env` 文件中将 `REDIS_HOST` 环境变量设置为 `valkey` 来连接该容器。

要从本地计算机连接到应用程序的 Valkey 数据库，可以使用图形化数据库管理工具（如 [TablePlus](https://tableplus.com)）。默认情况下，Valkey 数据库可通过 `localhost` 的 6379 端口访问。

### Meilisearch

如果在安装 Sail 时选择安装 [Meilisearch](https://www.meilisearch.com) 服务，应用程序的 `docker-compose.yml` 文件中将包含该强大的搜索引擎配置项，它与 [Laravel Scout](/docs/laravel/12.x/scout) 集成。
启动容器后，可以在应用程序中将 `MEILISEARCH_HOST` 环境变量设置为 `http://meilisearch:7700` 来连接 Meilisearch 实例。

从本地计算机访问 Meilisearch 的 Web 管理界面时，可在浏览器中打开 `http://localhost:7700`。

### Typesense

如果在安装 Sail 时选择安装 [Typesense](https://typesense.org) 服务，应用程序的 `docker-compose.yml` 文件中将包含该极速的开源搜索引擎配置项，它与 [Laravel Scout](/docs/laravel/12.x/scout#typesense) 原生集成。
启动容器后，可以在应用程序中设置以下环境变量来连接 Typesense 实例：

```ini
TYPESENSE_HOST=typesense
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
TYPESENSE_API_KEY=xyz
```



你可以通过本地计算机访问 Typesense 的 API，地址为：`http://localhost:8108`。

## 文件存储（File Storage）

如果你计划在生产环境中使用 Amazon S3 来存储文件，那么在安装 Sail 时可以选择安装 [MinIO](https://min.io) 服务。
MinIO 提供了一个兼容 S3 的 API，你可以在本地使用 Laravel 的 `s3` 文件存储驱动进行开发，而无需在生产环境的 S3 中创建“测试”存储桶。
如果在安装 Sail 时选择安装 MinIO，应用程序的 `docker-compose.yml` 文件中将会添加一个 MinIO 的配置部分。

默认情况下，应用程序的 `filesystems` 配置文件中已经包含了一个用于 `s3` 磁盘的配置。
除了用于与 Amazon S3 交互外，你也可以通过简单地修改相关环境变量的配置，使用该磁盘与任何兼容 S3 协议的文件存储服务（如 MinIO）进行交互。
例如，当使用 MinIO 时，文件系统的环境变量配置应如下所示：

```ini
FILESYSTEM_DISK=s3
AWS_ACCESS_KEY_ID=sail
AWS_SECRET_ACCESS_KEY=password
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=local
AWS_ENDPOINT=http://minio:9000
AWS_USE_PATH_STYLE_ENDPOINT=true
```

为了让 Laravel 的 Flysystem 集成在使用 MinIO 时生成正确的 URL，你应当定义 `AWS_URL` 环境变量，使其与应用程序的本地 URL 相匹配，并在路径中包含存储桶名称，例如：

```ini
AWS_URL=http://localhost:9000/local
```

你可以通过 MinIO 控制台来创建存储桶，该控制台可通过 `http://localhost:8900` 访问。
MinIO 控制台的默认用户名为 `sail`，默认密码为 `password`。

> [!警告]
> 当使用 MinIO 时，通过 `temporaryUrl` 方法生成临时存储 URL 的功能不受支持。



## 运行测试（Running Tests）

Laravel 开箱即用地提供了出色的测试支持，你可以使用 Sail 的 `test` 命令来运行应用程序的 [功能测试和单元测试](/docs/laravel/12.x/testing)。
任何被 Pest / PHPUnit 接受的命令行选项都可以传递给 `test` 命令，例如：

```shell
sail test

sail test --group orders
```

Sail 的 `test` 命令等同于运行 `test` 的 Artisan 命令：

```shell
sail artisan test
```

默认情况下，Sail 会创建一个专用的 `testing` 数据库，以防止测试干扰到当前数据库的实际数据状态。
在默认的 Laravel 安装中，Sail 还会自动配置你的 `phpunit.xml` 文件，使其在执行测试时使用该数据库：

```xml
<env name="DB_DATABASE" value="testing"/>
```

### Laravel Dusk

[Laravel Dusk](/docs/laravel/12.x/dusk) 提供了一个直观、易用的浏览器自动化和测试 API。
借助 Sail，你无需在本地计算机上安装 Selenium 或其他工具即可运行这些测试。
要开始使用，请取消注释应用程序 `docker-compose.yml` 文件中的 Selenium 服务配置：

```yaml
selenium:
    image: 'selenium/standalone-chrome'
    extra_hosts:
      - 'host.docker.internal:host-gateway'
    volumes:
        - '/dev/shm:/dev/shm'
    networks:
        - sail
```

接着，确保应用程序的 `docker-compose.yml` 文件中，`laravel.test` 服务包含对 `selenium` 的依赖项配置：

```yaml
depends_on:
    - mysql
    - redis
    - selenium
```

最后，你可以启动 Sail 并运行以下命令来执行 Dusk 测试套件：

```shell
sail dusk
```

#### Selenium on Apple Silicon



如果你的本地计算机搭载的是 Apple Silicon 芯片，那么你的 `selenium` 服务必须使用 `selenium/standalone-chromium` 镜像：

```yaml
selenium:
    image: 'selenium/standalone-chromium'
    extra_hosts:
        - 'host.docker.internal:host-gateway'
    volumes:
        - '/dev/shm:/dev/shm'
    networks:
        - sail
```

## 预览邮件（Previewing Emails）

Laravel Sail 默认的 `docker-compose.yml` 文件中包含一个 [Mailpit](https://github.com/axllent/mailpit) 服务配置项。
Mailpit 会拦截应用程序在本地开发期间发送的电子邮件，并提供一个方便的 Web 界面，使你可以在浏览器中预览这些邮件内容。
在使用 Sail 时，Mailpit 的默认主机名是 `mailpit`，默认端口是 `1025`：

```ini
MAIL_HOST=mailpit
MAIL_PORT=1025
MAIL_ENCRYPTION=null
```

当 Sail 正在运行时，你可以通过以下地址访问 Mailpit 的 Web 界面：
http://localhost:8025

## 容器命令行（Container CLI）

有时，你可能希望在应用程序的容器内启动一个 Bash 会话。
你可以使用 `shell` 命令连接到应用容器中，从而查看文件、已安装的服务，或在容器中执行任意 Shell 命令：

```shell
sail shell

sail root-shell
```

若要启动一个新的 [Laravel Tinker](https://github.com/laravel/tinker) 会话，可以执行以下命令：

```shell
sail tinker
```

## PHP 版本（PHP Versions）

Sail 目前支持通过 PHP 8.4、8.3、8.2、8.1 或 PHP 8.0 来运行你的应用程序。
默认情况下，Sail 使用 PHP 8.4。
如果你希望更改运行应用程序所使用的 PHP 版本，应在应用程序的 `docker-compose.yml` 文件中修改 `laravel.test` 容器的 `build` 定义部分：

```yaml
# PHP 8.4
context: ./vendor/laravel/sail/runtimes/8.4

# PHP 8.3
context: ./vendor/laravel/sail/runtimes/8.3

# PHP 8.2
context: ./vendor/laravel/sail/runtimes/8.2

# PHP 8.1
context: ./vendor/laravel/sail/runtimes/8.1

# PHP 8.0
context: ./vendor/laravel/sail/runtimes/8.0
```



此外，你可能希望在应用程序的 `docker-compose.yml` 文件中更新 `image` 名称，以反映应用程序所使用的 PHP 版本。该选项同样定义在 `docker-compose.yml` 文件中：

```yaml
image: sail-8.2/app
```

更新应用程序的 `docker-compose.yml` 文件后，你需要重新构建容器镜像：

```shell
sail build --no-cache

sail up
```

## Node 版本（Node Versions）

Sail 默认安装 Node 22。
如果希望更改在构建镜像时安装的 Node 版本，可以在应用程序的 `docker-compose.yml` 文件中更新 `laravel.test` 服务的 `build.args` 定义：

```yaml
build:
    args:
        WWWGROUP: '${WWWGROUP}'
        NODE_VERSION: '18'
```

更新应用程序的 `docker-compose.yml` 文件后，你需要重新构建容器镜像：

```shell
sail build --no-cache

sail up
```

## 共享你的网站（Sharing Your Site）

有时，你可能需要将你的网站公开分享，以便与同事一起预览，或用于测试应用程序的 webhook 集成。
要分享你的网站，可以使用 `share` 命令。执行该命令后，你将获得一个随机生成的 `laravel-sail.site` URL，通过它可以访问你的应用程序：

```shell
sail share
```

当通过 `share` 命令共享网站时，应在应用程序的 `bootstrap/app.php` 文件中使用 `trustProxies` 中间件方法来配置受信任代理。
否则，URL 生成辅助函数（如 `url` 和 `route`）将无法确定在生成 URL 时应使用的正确 HTTP 主机：

```php
->withMiddleware(function (Middleware $middleware) {
    $middleware->trustProxies(at: '*');
})
```



如果你希望为共享站点自定义子域名，可以在执行 `share` 命令时通过 `subdomain` 选项进行指定：

```shell
sail share --subdomain=my-sail-site
```

> [!注意]
> `share` 命令由 [Expose](https://github.com/beyondcode/expose) 提供支持，它是由 [BeyondCode](https://beyondco.de) 开发的一个开源隧道服务。


## 使用 Xdebug 进行调试（Debugging With Xdebug）

Laravel Sail 的 Docker 配置内置支持 [Xdebug](https://xdebug.org/)，这是一个广受欢迎且功能强大的 PHP 调试器。
要启用 Xdebug，请确保你已[发布 Sail 配置](#sail-customization)，然后在应用程序的 `.env` 文件中添加以下变量来配置 Xdebug：

```ini
SAIL_XDEBUG_MODE=develop,debug,coverage
```

接着，确保已发布的 `php.ini` 文件中包含以下配置，以便 Xdebug 在指定模式下启用：

```ini
[xdebug]
xdebug.mode=${XDEBUG_MODE}
```

修改 `php.ini` 文件后，请记得重新构建 Docker 镜像，以便更改生效：

```shell
sail build --no-cache
```

#### Linux 主机 IP 配置（Linux Host IP Configuration）

在内部，`XDEBUG_CONFIG` 环境变量被定义为 `client_host=host.docker.internal`，
这确保了 Xdebug 在 macOS 和 Windows（WSL2）环境下能够正确配置。

如果你的本地计算机运行的是 Linux 并且使用的是 Docker 20.10 或更高版本，`host.docker.internal` 是可用的，因此无需进行手动配置。

对于低于 20.10 的 Docker 版本，Linux 上不支持 `host.docker.internal`，
此时你需要手动定义主机 IP。
为此，可以在 `docker-compose.yml` 文件中定义一个自定义网络，并为容器配置静态 IP：

```yaml
networks:
  custom_network:
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  laravel.test:
    networks:
      custom_network:
        ipv4_address: 172.20.0.2
```



设置好静态 IP 之后，在应用程序的 `.env` 文件中定义 `SAIL_XDEBUG_CONFIG` 变量：

```ini
SAIL_XDEBUG_CONFIG="client_host=172.20.0.2"
```

### Xdebug 命令行使用（Xdebug CLI Usage）

在运行 Artisan 命令时，可以使用 `sail debug` 命令来启动调试会话：

```shell
# 在不使用 Xdebug 的情况下运行 Artisan 命令...
sail artisan migrate

# 使用 Xdebug 运行 Artisan 命令...
sail debug migrate
```

### Xdebug 浏览器调试（Xdebug Browser Usage）

若要在通过浏览器与应用程序交互时调试应用，请按照 [Xdebug 官方文档](https://xdebug.org/docs/step_debug#web-application) 中提供的说明，从 Web 浏览器启动 Xdebug 会话。

如果你使用的是 PhpStorm，请参考 JetBrains 官方文档中的[零配置调试指南](https://www.jetbrains.com/help/phpstorm/zero-configuration-debugging.html)。

> [!警告]
> Laravel Sail 依赖 `artisan serve` 来运行你的应用程序。
`artisan serve` 命令仅从 Laravel 版本 **8.53.0** 起支持 `XDEBUG_CONFIG` 和 `XDEBUG_MODE` 变量。
在旧版本的 Laravel（8.52.0 及以下）中，这些变量不受支持，因此无法建立调试连接。


## 自定义（Customization）

由于 Sail 只是基于 Docker 构建的，因此你几乎可以自定义其中的一切。
要发布 Sail 自带的 Dockerfile，可执行以下命令：

```shell
sail artisan sail:publish
```

执行该命令后，Laravel Sail 使用的 Dockerfile 以及其他配置文件会被放置在应用程序根目录下的 `docker` 文件夹中。

在自定义完 Sail 安装配置后，你可能希望在应用程序的 `docker-compose.yml` 文件中更改应用容器的镜像名称。完成修改后，使用 `build` 命令重新构建应用容器。

当你在同一台机器上使用 Sail 开发多个 Laravel 应用程序时，为应用镜像分配一个唯一的名称尤为重要：

```shell
sail build --no-cache
```
