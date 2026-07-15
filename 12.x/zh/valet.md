# Laravel Valet

- [简介](#introduction)
- [安装](#installation)
    - [升级 Valet](#upgrading-valet)
- [服务站点](#serving-sites)
    - [Park 命令](#the-park-command)
    - [Link 命令](#the-link-command)
    - [使用 TLS 加密站点](#securing-sites)
    - [设置默认站点](#serving-a-default-site)
    - [按站点指定 PHP 版本](#per-site-php-versions)
- [共享站点](#sharing-sites)
    - [在本地网络中共享站点](#sharing-sites-on-your-local-network)
- [站点特定环境变量](#site-specific-environment-variables)
- [代理服务](#proxying-services)
- [自定义 Valet 驱动](#custom-valet-drivers)
    - [本地驱动](#local-drivers)
- [其他 Valet 命令](#other-valet-commands)
- [Valet 的目录与文件](#valet-directories-and-files)
    - [磁盘访问权限](#disk-access)

<a name="introduction"></a>
## 简介

> [!NOTE]
> 想要在 macOS 或 Windows 上使用更简单的方式开发 Laravel 应用？ 可以看看 [Laravel Herd](https://herd.laravel.com). Herd 集成了 Laravel 开发所需的一切，包括 Valet、PHP 和 Composer。

[Laravel Valet](https://github.com/laravel/valet) 是一个为 macOS 极简主义者打造的开发环境。 Valet 会配置你的 Mac，使其在开机时始终在后台运行 [Nginx](https://www.nginx.com/) 。 接着，Valet 使用 [DnsMasq](https://en.wikipedia.org/wiki/Dnsmasq), 将所有 `*.test` 域名的请求代理到你本地安装的站点。

换句话说，Valet 是一个极其快速的 Laravel 开发环境，内存占用仅约 7 MB。 它不是 [Sail](/docs/laravel/12.x/sail) 或 [Homestead](/docs/laravel/12.x/homestead) 的完全替代品， 但如果你希望拥有灵活的基础配置、追求极致速度，或使用的是内存有限的设备，那么 Valet 是一个很棒的选择。

Valet 开箱即支持以下（但不限于）框架和系统：

<style>
    #valet-support > ul {
        column-count: 3; -moz-column-count: 3; -webkit-column-count: 3;
        line-height: 1.9;
    }
</style>

<div id="valet-support" markdown="1">

- [Laravel](https://laravel.com)
- [Bedrock](https://roots.io/bedrock/)
- [CakePHP 3](https://cakephp.org)
- [ConcreteCMS](https://www.concretecms.com/)
- [Contao](https://contao.org/en/)
- [Craft](https://craftcms.com)
- [Drupal](https://www.drupal.org/)
- [ExpressionEngine](https://www.expressionengine.com/)
- [Jigsaw](https://jigsaw.tighten.co)
- [Joomla](https://www.joomla.org/)
- [Katana](https://github.com/themsaid/katana)
- [Kirby](https://getkirby.com/)
- [Magento](https://magento.com/)
- [OctoberCMS](https://octobercms.com/)
- [Sculpin](https://sculpin.io/)
- [Slim](https://www.slimframework.com)
- [Statamic](https://statamic.com)
- Static HTML
- [Symfony](https://symfony.com)
- [WordPress](https://wordpress.org)
- [Zend](https://framework.zend.com)

</div>



不过，你也可以通过 [自定义驱动 ](#custom-valet-drivers) 来扩展 Valet 的功能。

<a name="installation"></a>
## 安装

> [!WARNING]
> Valet 只能运行在 macOS 上，并依赖 [Homebrew](https://brew.sh/)。 在安装之前，请确保没有其他程序（如 Apache 或 Nginx）占用了本机的 80 端口。

在开始之前，请使用以下命令确保 Homebrew 是最新的：

```shell
brew update
```

接着，通过 Homebrew 安装 PHP：

```shell
brew install php
```

安装完 PHP 后，就可以安装 [Composer 包管理器](https://getcomposer.org)。 另外，请确保你的系统环境变量 "PATH" 中包含目录 `$HOME/.composer/vendor/bin` 。 Composer 安装完成后，就可以使用以下命令全局安装 Laravel Valet：

```shell
composer global require laravel/valet
```

运行以下命令，Valet 会自动配置并安装自身以及 DnsMasq。 除此之外，Valet 依赖的守护进程也会被配置为随系统启动自动运行：

```shell
valet install
```

安装完成后，你可以尝试在终端中使用 `ping foobar.test` 来测试任意 `*.test` 结尾的域名。如果安装正确，该域名应该会返回 `127.0.0.1` 的响应。

Valet 会在每次开机时自动启动所需的服务。

<a name="php-versions"></a>
#### PHP 版本管理

> [!NOTE]
> 与其修改全局 PHP 版本，不如使用 Valet 的 `isolate` [命令](#per-site-php-versions) 为每个站点指定 PHP 版本。

Valet 允许你通过以下命令切换 PHP 版本。如果指定版本尚未安装，Valet 会使用 Homebrew 自动安装：

```shell
valet use php@8.2

valet use php
```



你也可以在项目根目录创建一个 `.valetrc` 文件。该文件应包含该站点所需使用的 PHP 版本，例如：

```shell
php=php@8.2
```

一旦创建好此文件，你只需执行 `valet use` 命令，Valet 会读取 .valetrc 文件，自动确定该站点所需的 PHP 版本。

> [!WARNING]
> 即使你安装了多个 PHP 版本，Valet 仍然一次只能运行一个 PHP 版本。

<a name="database"></a>
#### 数据库

如果你的应用需要数据库，可以试试 [DBngin](https://dbngin.com), 它是一个免费的、集成的数据库管理工具，支持 MySQL、PostgreSQL 和 Redis。安装 DBngin 后，你可以使用 `127.0.0.1` 地址连接数据库，用户名为 `root`，密码为空。

<a name="resetting-your-installation"></a>
#### 重置 Valet 安装

如果你在使用 Valet 的过程中遇到问题，可以尝试先执行：`composer global require laravel/valet` 然后再次运行： `valet install` 这将重置你的安装环境，通常能解决很多问题。 在少数情况下，你可能需要进行 "强制重置"， 使用以下命令： `valet uninstall --force` 和 `valet install`.

<a name="upgrading-valet"></a>
### 升级 Valet

你可以使用以下命令来更新你的 Valet 安装： `composer global require laravel/valet` 。 升级完成后，建议再次运行： `valet install` 命令以便 Valet 在有需要时自动更新配置文件。

<a name="upgrading-to-valet-4"></a>
#### 升级到 Valet 4

如果你正在从 Valet 3 升级到 Valet 4，请按照以下步骤正确进行升级：

<div class="content-list" markdown="1">

- 如果你之前使用 `.valetphprc` 文件为站点设置 PHP 版本， 请将其重命名为 `.valetrc`。并在文件内容前添加 `php=` 前缀。
- 如果你使用了自定义驱动，请更新命名空间、类扩展、类型提示和返回类型提示，以符合新的驱动系统规范。你可以参考 Valet 的 示例驱动 [SampleValetDriver](https://github.com/laravel/valet/blob/d7787c025e60abc24a5195dc7d4c5c6f2d984339/cli/stubs/SampleValetDriver.php) 。
- 如果你使用 PHP 7.1 到 7.4 来服务站点，请确保仍通过 Homebrew 安装一个 PHP 8.0 或以上的版本。即使该版本不是你的主版本，Valet 的某些脚本也会依赖该版本运行。

</div>



<a name="serving-sites"></a>
## 服务站点

当你完成 Valet 的安装后，就可以开始运行你的 Laravel 应用了。Valet 提供了两个命令来帮助你服务本地应用：`park` 和 `link`.

<a name="the-park-command"></a>
### `park` 命令

`park` 命令用于注册一个包含多个项目的目录。 一旦你将某个目录通过 `park` 命令注册到 Valet, 该目录下的每一个子目录都可以通过浏览器访问，形式为 `http://<directory-name>.test`:

```shell
cd ~/Sites

valet park
```

就是这么简单。现在你在这个 "parked" 目录中创建的任何应用，都可以通过 `http://<directory-name>.test` 来访问。例如， i如果该目录下有一个名为 "laravel" 的子目录, 该目录中的应用就可以通过 `http://laravel.test` 访问。 此外，Valet 还自动支持通配子域名，例如： (`http://foo.laravel.test`) 也可以正常访问。

<a name="the-link-command"></a>
### `link` 命令

`link` 命令也可以用来服务 Laravel 应用。当你只想单独服务某一个项目目录，而不是整个目录时，link 是一个更合适的选择：

```shell
cd ~/Sites/laravel

valet link
```

一旦你使用 `link` 命令将该项目链接到 Valet，就可以通过其目录名访问它。例如，上面的项目将可以通过 `http://laravel.test`访问。 同样地，Valet 也支持该站点的通配子域名访问，如： (`http://foo.laravel.test`).

如果你希望用另一个自定义的域名来访问这个站点，可以在 `link` 命令中指定域名，例如，以下命令会让该应用可以通过 `http://application.test`访问。

```shell
cd ~/Sites/laravel

valet link application
```



当然，你也可以使用 `link` 命令将应用配置为子域名的形式：

```shell
valet link api.application
```

你可以使用 `links` 命令查看所有已链接的目录列表：

```shell
valet links
```

要删除某个站点的符号链接，可以使用 `unlink` 命令：

```shell
cd ~/Sites/laravel

valet unlink
```

<a name="securing-sites"></a>
### 使用 TLS 加密站点

默认情况下，Valet 是通过 HTTP 提供站点服务。但如果你希望通过 加密的 TLS（支持 HTTP/2） 来访问站点，可以使用 `secure` 命令。 例如，如果你的站点域名为 `laravel.test`， 你可以运行以下命令来启用 HTTPS：

```shell
valet secure laravel
```

若你希望取消加密访问（即恢复为普通 HTTP），可以使用 `unsecure` 命令。该命令与 `secure` 相似，需要指定要取消加密的站点：

```shell
valet unsecure laravel
```

<a name="serving-a-default-site"></a>
### 设置默认站点

有时，你可能希望在访问未知的 `test` 域名时不返回 404 页面，而是跳转到一个 "默认" 站点。 你可以在配置文件 `~/.config/valet/config.json` 中添加一个 `default` 选项，配置默认站点路径，例如：

    "default": "/Users/Sally/Sites/example-site",

<a name="per-site-php-versions"></a>
### 按站点指定 PHP 版本

默认情况下，Valet 使用你系统中全局安装的 PHP 版本来运行站点。但如果你需要在不同的站点中使用不同版本的 PHP，可以使用 `isolate` 命令为特定站点指定 PHP 版本。 `isolate` 命令会将当前目录下的站点配置为使用指定的 PHP 版本：

```shell
cd ~/Sites/example-site

valet isolate php@8.0
```



如果你的网站名称与包含它的目录名称不一致，你可以使用 `--site` 选项来指定站点名称：

```shell
valet isolate php@8.0 --site="site-name"
```

为了方便起见，你可以使用 `valet php`、`composer` 和 `which-php` 命令，将调用代理到基于站点配置的 PHP 版本所对应的 PHP CLI 或工具：

```shell
valet php
valet composer
valet which-php
```

你可以执行 `isolated` 命令来显示所有已隔离站点及其 PHP 版本的列表：

```shell
valet isolated
```

要将站点恢复为 Valet 全局安装的 PHP 版本，你可以在站点的根目录中运行 `unisolate` 命令：

```shell
valet unisolate
```

## 共享站点

Valet 包含一个命令，可以将你的本地站点与外界共享，从而提供一种简单的方式来在移动设备上测试站点，或与团队成员和客户共享。

开箱即用的情况下，Valet 支持通过 ngrok 或 Expose 来共享站点。在共享站点之前，你应该使用 `share-tool` 命令更新 Valet 配置，指定 `ngrok`、`expose` 或 `cloudflared`：

```shell
valet share-tool ngrok
```

如果你选择的工具尚未通过 Homebrew（用于 ngrok 和 cloudflared）或 Composer（用于 Expose）安装，Valet 会自动提示你安装它。当然，在开始共享站点之前，你需要先验证 ngrok 或 Expose 的账户。

要共享站点，请在终端中导航到站点的目录并运行 Valet 的 `share` 命令。一个可公开访问的 URL 会被放入剪贴板，可以直接粘贴到浏览器中，或与团队共享：

```shell
cd ~/Sites/laravel

valet share
```



要停止共享你的网站，你可以按下 `Control + C`。

> [!警告]
> 如果你正在使用自定义 DNS 服务器（例如 `1.1.1.1`），ngrok 共享可能无法正常工作。如果在你的电脑上出现这种情况，请打开 Mac 的系统设置，进入 **网络设置**，再打开 **高级设置**，然后进入 **DNS 标签页**，并将 `127.0.0.1` 添加为第一个 DNS 服务器。

#### 通过 Ngrok 共享站点

使用 ngrok 共享站点需要你先[创建一个 ngrok 账户](https://dashboard.ngrok.com/signup?utm_source=chatgpt.com)，并且[设置一个认证令牌](https://dashboard.ngrok.com/get-started/your-authtoken?utm_source=chatgpt.com)。一旦你有了认证令牌，就可以用该令牌更新你的 Valet 配置：

```shell
valet set-ngrok-token YOUR_TOKEN_HERE
```


> [!注意]
> 你可以在 `share` 命令中传递额外的 ngrok 参数，比如：`valet share --region=eu `
更多信息请参考 [ngrok 文档](https://ngrok.com/docs?utm_source=chatgpt.com)。

#### 通过 Expose 共享站点

使用 Expose 共享站点需要你先[创建一个 Expose 账户](https://expose.dev/register?utm_source=chatgpt.com)，并且[通过认证令牌来验证 Expose](https://expose.dev/docs/getting-started/getting-your-token?utm_source=chatgpt.com)。

你可以查阅 [Expose 文档](https://expose.dev/docs?utm_source=chatgpt.com)，了解它所支持的额外命令行参数信息。

### 在本地网络中共享站点

Valet 默认会将传入流量限制在内部的 `127.0.0.1` 接口上，以防止你的开发机器暴露在来自互联网的安全风险中。

如果你希望允许本地网络中的其他设备通过你机器的 IP 地址访问 Valet 站点（例如：`192.168.1.10/application.test`），你需要手动编辑该站点对应的 Nginx 配置文件，去掉 `listen` 指令上的限制。你应当移除端口 80 和 443 的 `listen` 指令中的 `127.0.0.1:` 前缀。



如果你没有在项目上运行过 `valet secure`，你可以通过编辑 `/usr/local/etc/nginx/valet/valet.conf` 文件来为所有非 HTTPS 站点打开网络访问。
但是，如果你通过 HTTPS 提供项目站点服务（即你已经为该站点运行过 `valet secure`），那么你应该编辑 `~/.config/valet/Nginx/app-name.test` 文件。

更新 Nginx 配置后，运行 `valet restart` 命令以应用配置更改。

## 针对站点的环境变量

某些使用其他框架的应用可能依赖于服务器环境变量，但并未提供在项目内部配置这些变量的方式。
Valet 允许你通过在项目根目录中添加 `.valet-env.php` 文件来配置站点专用的环境变量。
该文件应返回一个 **站点 / 环境变量** 对应的数组，这些变量会被添加到全局的 `$_SERVER` 数组中，针对数组中指定的每个站点生效：

```php
<?php

return [
    // 为 laravel.test 站点设置 $_SERVER['key'] 为 "value"...
    'laravel' => [
        'key' => 'value',
    ],

    // 为所有站点设置 $_SERVER['key'] 为 "value"...
    '*' => [
        'key' => 'value',
    ],
];
```

## 服务代理

有时你可能希望将某个 Valet 域名代理到本地机器上的另一个服务。
例如，你可能偶尔需要运行 Valet，同时又在 Docker 中运行一个独立的站点；然而，Valet 和 Docker 不能同时绑定到端口 80。

为了解决这个问题，你可以使用 `proxy` 命令来生成代理。
例如，你可以将来自 `http://elasticsearch.test` 的所有流量代理到 `http://127.0.0.1:9200`：

```shell
# 通过 HTTP 代理...
valet proxy elasticsearch http://127.0.0.1:9200

# 通过 TLS + HTTP/2 代理...
valet proxy elasticsearch http://127.0.0.1:9200 --secure
```



你可以使用 `unproxy` 命令来移除一个代理：

```shell
valet unproxy elasticsearch
```

你可以使用 `proxies` 命令来列出所有被代理的站点配置：

```shell
valet proxies
```

## 自定义 Valet 驱动

你可以编写自己的 Valet “驱动”来为那些 Valet 并未原生支持的框架或 CMS 上运行的 PHP 应用提供服务。
当你安装 Valet 时，会创建一个 `~/.config/valet/Drivers` 目录，其中包含一个 `SampleValetDriver.php` 文件。该文件包含了一个示例驱动的实现，用于演示如何编写自定义驱动。
编写驱动只需要实现三个方法：`serves`、`isStaticFile` 和 `frontControllerPath`。
这三个方法都会接收 `$sitePath`、`$siteName` 和 `$uri` 作为参数。
-   `$sitePath` 是你机器上被服务站点的完整路径，例如 `/Users/Lisa/Sites/my-project`。
-   `$siteName` 是域名中的 “主机名 / 站点名” 部分（`my-project`）。
-   `$uri` 是传入请求的 URI（`/foo/bar`）。
完成自定义 Valet 驱动后，请将其放入 `~/.config/valet/Drivers` 目录中，并使用 `FrameworkValetDriver.php` 的命名约定。
例如，如果你正在为 WordPress 编写一个自定义 Valet 驱动，那么文件名应该是 `WordPressValetDriver.php`。

下面让我们来看一个示例，实现你自定义 Valet 驱动所需的每个方法。

#### `serves` 方法

如果你的驱动应该处理传入的请求，`serves` 方法应返回 `true`。否则，该方法应返回 `false`。
因此，在此方法中，你应当尝试判断给定的 `$sitePath` 是否包含你要提供服务的那种类型的项目。



例如，假设我们正在编写一个 `WordPressValetDriver`。我们的 `serves` 方法可能看起来像这样：

```php
/**
 * 判断该驱动是否处理请求
 */
public function serves(string $sitePath, string $siteName, string $uri): bool
{
    return is_dir($sitePath.'/wp-admin');
}
```

#### `isStaticFile` 方法

`isStaticFile` 方法应当判断传入的请求是否是一个“静态”文件，例如图片或样式表。
如果请求的确是静态文件，该方法应返回该静态文件在磁盘上的完整路径。
如果传入的请求不是静态文件，则方法应返回 `false`：

```php
/**
 * 判断传入请求是否为静态文件
 *
 * @return string|false
 */
public function isStaticFile(string $sitePath, string $siteName, string $uri)
{
    if (file_exists($staticFilePath = $sitePath.'/public/'.$uri)) {
        return $staticFilePath;
    }

    return false;
}
```

> [!警告]
> `isStaticFile` 方法只会在以下条件下被调用：
-   `serves` 方法对传入请求返回了 `true`；
-   并且请求的 URI 不是 `/`。

#### `frontControllerPath` 方法

`frontControllerPath` 方法应返回应用程序“前端控制器”（通常是 `index.php` 文件或等效文件）的完整路径：

```php
/**
 * 获取应用程序前端控制器的完整路径
 */
public function frontControllerPath(string $sitePath, string $siteName, string $uri): string
{
    return $sitePath.'/public/index.php';
}
```

### 本地驱动（Local Drivers）

如果你希望只为单个应用定义一个自定义的 Valet 驱动，可以在应用程序根目录下创建一个 `LocalValetDriver.php` 文件。

你的自定义驱动可以继承基础的 `ValetDriver` 类，或者继承一个现有的特定应用驱动，例如 `LaravelValetDriver`：

```php
use Valet\Drivers\LaravelValetDriver;

class LocalValetDriver extends LaravelValetDriver
{
    /**
     * 判断该驱动是否处理请求。
     */
    public function serves(string $sitePath, string $siteName, string $uri): bool
    {
        return true;
    }

    /**
     * 获取应用程序前端控制器的完整路径。
     */
    public function frontControllerPath(string $sitePath, string $siteName, string $uri): string
    {
        return $sitePath.'/public_html/index.php';
    }
}
```



## 其他 Valet 命令

<div class="overflow-auto">

| 命令                        | 描述                                                      |
| ------------------------- | ------------------------------------------------------- |
| `valet list`              | 显示所有 Valet 命令的列表。                                       |
| `valet diagnose`          | 输出诊断信息，以帮助调试 Valet。                                     |
| `valet directory-listing` | 确定目录列表行为。默认是 "off"，即为目录渲染 404 页面。                       |
| `valet forget`            | 在一个「停放」目录中运行此命令，可将其从停放目录列表中移除。                          |
| `valet log`               | 查看由 Valet 服务写入的日志列表。                                    |
| `valet paths`             | 查看所有已「停放」的路径。                                           |
| `valet restart`           | 重启 Valet 守护进程。                                          |
| `valet start`             | 启动 Valet 守护进程。                                          |
| `valet stop`              | 停止 Valet 守护进程。                                          |
| `valet trust`             | 为 Brew 和 Valet 添加 sudoers 文件，使 Valet 命令在运行时无需输入密码。      |
| `valet uninstall`         | 卸载 Valet：显示手动卸载的说明。传递 `--force` 选项可强制删除所有与 Valet 相关的资源。 |

</div>

## Valet 目录与文件

在排查 Valet 环境问题时，以下目录和文件信息可能会对你有所帮助：

#### `~/.config/valet`

包含了 Valet 的所有配置。你可能希望对该目录进行备份。

#### `~/.config/valet/dnsmasq.d/`

该目录包含 DNSMasq 的配置。

#### `~/.config/valet/Drivers/`

该目录包含 Valet 的驱动。驱动决定了某个特定框架 / CMS 的运行方式。

#### `~/.config/valet/Nginx/`

该目录包含所有 Valet 的 Nginx 站点配置。这些文件会在运行 `install` 和 `secure` 命令时被重建。

#### `~/.config/valet/Sites/`

该目录包含所有 [已链接项目](#the-link-command) 的符号链接。



#### `~/.config/valet/config.json`

此文件是 Valet 的主配置文件。

#### `~/.config/valet/valet.sock`

此文件是 Valet 的 Nginx 安装所使用的 PHP-FPM 套接字。只有在 PHP 正常运行时，该文件才会存在。

#### `~/.config/valet/Log/fpm-php.www.log`

此文件是用户级的 PHP 错误日志。

#### `~/.config/valet/Log/nginx-error.log`

此文件是用户级的 Nginx 错误日志。

#### `/usr/local/var/log/php-fpm.log`

此文件是系统级的 PHP-FPM 错误日志。

#### `/usr/local/var/log/nginx`

此目录包含 Nginx 的访问日志和错误日志。

#### `/usr/local/etc/php/X.X/conf.d`

此目录包含各种 PHP 配置的 `*.ini` 文件。

#### `/usr/local/etc/php/X.X/php-fpm.d/valet-fpm.conf`

此文件是 PHP-FPM 的进程池配置文件。

#### `~/.composer/vendor/laravel/valet/cli/stubs/secure.valet.conf`

此文件是默认的 Nginx 配置，用于为你的网站生成 SSL 证书。

### 磁盘访问权限

自 macOS 10.14 起，[对某些文件和目录的访问默认被限制](https://manuals.info.apple.com/MANUALS/1000/MA1902/en_US/apple-platform-security-guide.pdf?utm_source=chatgpt.com)。这些受限制的目录包括 **桌面（Desktop）**、**文稿（Documents）** 和 **下载（Downloads）**。此外，网络卷和可移动卷的访问也受到限制。因此，Valet 建议你将站点文件夹放在这些受保护位置之外。

但是，如果你希望从这些目录中提供站点服务，你需要授予 Nginx「完整磁盘访问权限（Full Disk Access）」。否则，Nginx 在提供静态资源时可能会遇到服务器错误或其他不可预期的行为。通常情况下，macOS 会自动提示你授予 Nginx 对这些目录的完全访问权限。你也可以手动前往 **系统偏好设置（System Preferences） > 安全性与隐私（Security & Privacy） > 隐私（Privacy）** 并选择 **完整磁盘访问（Full Disk Access）**，然后在主窗口中启用任何 `nginx` 条目。

