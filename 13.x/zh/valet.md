# Laravel Valet

- [简介](#introduction)
- [安装](#installation)
    - [升级 Valet](#upgrading-valet)
- [服务站点](#serving-sites)
    - [`park` 命令](#the-park-command)
    - [`link` 命令](#the-link-command)
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
> 想要在 macOS 或 Windows 上以更简单的方式开发 Laravel 应用？不妨试试 [Laravel Herd](https://herd.laravel.com)。Herd 包含开始 Laravel 开发所需的一切，包括 Valet、PHP 和 Composer。

[Laravel Valet](https://github.com/laravel/valet) 是一个为 macOS 极简主义者打造的开发环境。Laravel Valet 会配置你的 Mac，使 [Nginx](https://www.nginx.com/) 在机器启动时始终于后台运行。然后，Valet 使用 [DnsMasq](https://en.wikipedia.org/wiki/Dnsmasq) 将所有对 `*.test` 域名的请求代理到本地安装的站点。

换句话说，Valet 是一个速度极快的 Laravel 开发环境，内存占用仅约 7 MB。Valet 不能完全替代 [Sail](/docs/{{version}}/sail) 或 [Homestead](/docs/{{version}}/homestead)，但如果你需要灵活的基础功能、追求极致速度，或正在使用内存有限的机器，它会是一个很好的选择。

Valet 开箱即支持以下框架和系统（但不限于这些）：

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
- 静态 HTML
- [Symfony](https://symfony.com)
- [WordPress](https://wordpress.org)
- [Zend](https://framework.zend.com)

</div>

此外，你还可以使用自己的[自定义驱动](#custom-valet-drivers)来扩展 Valet。

<a name="installation"></a>
## 安装

> [!WARNING]
> Valet 需要 macOS 和 [Homebrew](https://brew.sh/)。安装前，请确保没有 Apache 或 Nginx 等其他程序占用本机的 80 端口。

首先，你需要使用 `update` 命令确保 Homebrew 为最新版本：

```shell
brew update
```

接下来，使用 Homebrew 安装 PHP：

```shell
brew install php
```

安装 PHP 后，就可以安装 [Composer 包管理器](https://getcomposer.org)。此外，请确保系统的 `PATH` 环境变量中包含 `$HOME/.composer/vendor/bin` 目录。安装 Composer 后，可以将 Laravel Valet 安装为全局 Composer 软件包：

```shell
composer global require laravel/valet
```

最后，执行 Valet 的 `install` 命令。此命令将配置并安装 Valet 和 DnsMasq，还会将 Valet 依赖的守护进程配置为随系统启动：

```shell
valet install
```

Valet 安装完成后，可以在终端中使用 `ping foobar.test` 之类的命令 ping 任意 `*.test` 域名。如果 Valet 安装正确，你应该会看到该域名从 `127.0.0.1` 返回响应。

每次机器启动时，Valet 都会自动启动所需的服务。

<a name="php-versions"></a>
#### PHP 版本

> [!NOTE]
> 你可以通过 `isolate` [命令](#per-site-php-versions)让 Valet 为每个站点使用不同的 PHP 版本，而不必修改全局 PHP 版本。

Valet 允许你使用 `valet use php@version` 命令切换 PHP 版本。如果尚未安装指定的 PHP 版本，Valet 会通过 Homebrew 进行安装：

```shell
valet use php@8.2

valet use php
```

你也可以在项目根目录中创建 `.valetrc` 文件。该文件应包含站点需要使用的 PHP 版本：

```shell
php=php@8.2
```

创建该文件后，只需执行 `valet use` 命令，该命令便会读取文件并确定站点所需的 PHP 版本。

> [!WARNING]
> 即使安装了多个 PHP 版本，Valet 一次也只能使用一个 PHP 版本提供服务。

<a name="database"></a>
#### 数据库

如果你的应用需要数据库，可以试试 [DBngin](https://dbngin.com)。它是一款免费的多合一数据库管理工具，支持 MySQL、PostgreSQL 和 Redis。安装 DBngin 后，可以使用 `root` 用户名和空密码连接 `127.0.0.1` 上的数据库。

<a name="resetting-your-installation"></a>
#### 重置安装

如果 Valet 无法正常运行，可以先执行 `composer global require laravel/valet` 命令，再执行 `valet install`。这将重置安装并解决多种问题。在极少数情况下，可能需要先执行 `valet uninstall --force`，再执行 `valet install`，以「硬重置」Valet。

<a name="upgrading-valet"></a>
### 升级 Valet

你可以在终端中执行 `composer global require laravel/valet` 命令来更新 Valet。升级后，最好运行 `valet install` 命令，以便 Valet 在必要时进一步升级配置文件。

<a name="upgrading-to-valet-4"></a>
#### 升级到 Valet 4

如果要从 Valet 3 升级到 Valet 4，请执行以下步骤以正确升级 Valet：

<div class="content-list" markdown="1">

- 如果添加过 `.valetphprc` 文件来自定义站点的 PHP 版本，请将每个 `.valetphprc` 文件重命名为 `.valetrc`，然后在 `.valetrc` 文件的现有内容前添加 `php=`。
- 更新所有自定义驱动，使其命名空间、继承关系、类型提示和返回类型提示符合新的驱动系统。你可以参考 Valet 的 [SampleValetDriver](https://github.com/laravel/valet/blob/d7787c025e60abc24a5195dc7d4c5c6f2d984339/cli/stubs/SampleValetDriver.php)。
- 如果使用 PHP 7.1 至 7.4 提供站点服务，请确保仍通过 Homebrew 安装 PHP 8.0 或更高版本。即使它不是当前主要链接的版本，Valet 也会使用该版本运行部分脚本。

</div>

<a name="serving-sites"></a>
## 服务站点

安装 Valet 后，就可以开始为 Laravel 应用提供服务。Valet 提供了两个命令来帮助你提供应用服务：`park` 和 `link`。

<a name="the-park-command"></a>
### `park` 命令

`park` 命令用于注册机器上存放应用的目录。使用 Valet「停放」该目录后，其中的所有目录都可以在 Web 浏览器中通过 `http://<directory-name>.test` 访问：

```shell
cd ~/Sites

valet park
```

就这么简单。现在，在「停放」目录中创建的任何应用都会自动按照 `http://<directory-name>.test` 约定提供服务。例如，如果停放目录中包含名为「laravel」的目录，该目录中的应用便可以通过 `http://laravel.test` 访问。此外，Valet 还会自动允许你使用通配符子域名（`http://foo.laravel.test`）访问该站点。

<a name="the-link-command"></a>
### `link` 命令

`link` 命令也可以用于提供 Laravel 应用服务。当你只想提供目录中的单个站点，而不是整个目录时，此命令会很有用：

```shell
cd ~/Sites/laravel

valet link
```

使用 `link` 命令将应用链接到 Valet 后，可以通过应用的目录名称访问它。因此，上例中链接的站点可以通过 `http://laravel.test` 访问。此外，Valet 还会自动允许你使用通配符子域名（`http://foo.laravel.test`）访问该站点。

如果要使用不同的主机名提供应用服务，可以将主机名传给 `link` 命令。例如，可以运行以下命令，使应用能够通过 `http://application.test` 访问：

```shell
cd ~/Sites/laravel

valet link application
```

当然，你也可以使用 `link` 命令在子域名上提供应用服务：

```shell
valet link api.application
```

可以执行 `links` 命令显示所有已链接目录的列表：

```shell
valet links
```

可以使用 `unlink` 命令删除站点的符号链接：

```shell
cd ~/Sites/laravel

valet unlink
```

<a name="securing-sites"></a>
### 使用 TLS 加密站点

默认情况下，Valet 通过 HTTP 提供站点服务。但是，如果要使用 HTTP/2 通过加密的 TLS 提供站点服务，可以使用 `secure` 命令。例如，如果 Valet 通过 `laravel.test` 域名提供站点服务，应运行以下命令保护该站点：

```shell
valet secure laravel
```

若要「取消保护」站点并恢复通过普通 HTTP 提供流量，请使用 `unsecure` 命令。与 `secure` 命令一样，此命令接受要取消保护的主机名：

```shell
valet unsecure laravel
```

<a name="serving-a-default-site"></a>
### 设置默认站点

有时，你可能希望将 Valet 配置为在访问未知的 `test` 域名时提供一个「默认」站点，而不是返回 `404`。为此，可以在 `~/.config/valet/config.json` 配置文件中添加 `default` 选项，其值为作为默认站点提供服务的站点路径：

    "default": "/Users/Sally/Sites/example-site",

<a name="per-site-php-versions"></a>
### 按站点指定 PHP 版本

默认情况下，Valet 使用全局 PHP 安装来提供站点服务。但是，如果不同站点需要多个 PHP 版本，可以使用 `isolate` 命令指定特定站点应使用的 PHP 版本。`isolate` 命令会将 Valet 配置为对当前工作目录中的站点使用指定的 PHP 版本：

```shell
cd ~/Sites/example-site

valet isolate php@8.0
```

如果站点名称与其所在目录的名称不同，可以使用 `--site` 选项指定站点名称：

```shell
valet isolate php@8.0 --site="site-name"
```

为方便起见，可以使用 `valet php`、`composer` 和 `which-php` 命令，根据站点配置的 PHP 版本，将调用代理到相应的 PHP CLI 或工具：

```shell
valet php
valet composer
valet which-php
```

可以执行 `isolated` 命令显示所有已隔离站点及其 PHP 版本的列表：

```shell
valet isolated
```

若要让站点恢复使用 Valet 全局安装的 PHP 版本，可以在站点根目录中调用 `unisolate` 命令：

```shell
valet unisolate
```

<a name="sharing-sites"></a>
## 共享站点

Valet 提供了将本地站点共享到互联网的命令，让你能够轻松地在移动设备上测试站点，或与团队成员和客户共享站点。

Valet 开箱即支持通过 ngrok 或 Expose 共享站点。共享站点前，应使用 `share-tool` 命令更新 Valet 配置，并指定 `ngrok`、`expose` 或 `cloudflared`：

```shell
valet share-tool ngrok
```

如果选择的工具尚未通过 Homebrew（ngrok 和 cloudflared）或 Composer（Expose）安装，Valet 会自动提示你安装。当然，在开始共享站点前，ngrok 和 Expose 都要求你验证相应的账户。

若要共享站点，请在终端中进入该站点的目录，然后运行 Valet 的 `share` 命令。一个可公开访问的 URL 将被复制到剪贴板，你可以直接将其粘贴到浏览器中，或与团队共享：

```shell
cd ~/Sites/laravel

valet share
```

若要停止共享站点，可以按 `Control + C`。

> [!WARNING]
> 如果使用自定义 DNS 服务器（例如 `1.1.1.1`），ngrok 共享可能无法正常工作。如果你的机器遇到这种情况，请打开 Mac 的系统设置，进入网络设置并打开高级设置，然后进入 DNS 标签页，将 `127.0.0.1` 添加为第一个 DNS 服务器。

<a name="sharing-sites-via-ngrok"></a>
#### 通过 Ngrok 共享站点

使用 ngrok 共享站点前，需要[创建 ngrok 账户](https://dashboard.ngrok.com/signup)并[设置身份验证令牌](https://dashboard.ngrok.com/get-started/your-authtoken)。获取身份验证令牌后，可以使用该令牌更新 Valet 配置：

```shell
valet set-ngrok-token YOUR_TOKEN_HERE
```

> [!NOTE]
> 可以向 share 命令传递其他 ngrok 参数，例如 `valet share --region=eu`。有关更多信息，请参阅 [ngrok 文档](https://ngrok.com/docs)。

<a name="sharing-sites-via-expose"></a>
#### 通过 Expose 共享站点

使用 Expose 共享站点前，需要[创建 Expose 账户](https://expose.dev/register)，并[通过身份验证令牌进行 Expose 身份验证](https://expose.dev/docs/getting-started/getting-your-token)。

你可以查阅 [Expose 文档](https://expose.dev/docs)，了解其支持的其他命令行参数。

<a name="sharing-sites-on-your-local-network"></a>
### 在本地网络中共享站点

Valet 默认将传入流量限制在内部 `127.0.0.1` 接口上，以免开发机器暴露于来自互联网的安全风险。

如果要允许本地网络中的其他设备通过你机器的 IP 地址访问机器上的 Valet 站点（例如 `192.168.1.10/application.test`），则需要手动编辑该站点对应的 Nginx 配置文件，移除 `listen` 指令上的限制。对于 80 和 443 端口，应移除 `listen` 指令中的 `127.0.0.1:` 前缀。

如果没有对项目运行过 `valet secure`，可以编辑 `/usr/local/etc/nginx/valet/valet.conf` 文件，为所有非 HTTPS 站点开放网络访问。但是，如果通过 HTTPS 提供项目站点服务（即已对站点运行过 `valet secure`），则应编辑 `~/.config/valet/Nginx/app-name.test` 文件。

更新 Nginx 配置后，请运行 `valet restart` 命令应用配置更改。

<a name="site-specific-environment-variables"></a>
## 站点特定环境变量

使用其他框架的某些应用可能依赖服务器环境变量，但未提供在项目中配置这些变量的方法。Valet 允许你在项目根目录中添加 `.valet-env.php` 文件，以配置站点特定的环境变量。该文件应返回一个由站点和环境变量构成的数组；对于数组中指定的每个站点，这些变量都会被添加到全局 `$_SERVER` 数组中：

```php
<?php

return [
    // 为 laravel.test 站点将 $_SERVER['key'] 设置为 "value"...
    'laravel' => [
        'key' => 'value',
    ],

    // 为所有站点将 $_SERVER['key'] 设置为 "value"...
    '*' => [
        'key' => 'value',
    ],
];
```

<a name="proxying-services"></a>
## 代理服务

有时，你可能希望将 Valet 域名代理到本地机器上的其他服务。例如，你可能需要在运行 Valet 的同时，在 Docker 中运行另一个独立站点；但是，Valet 和 Docker 无法同时绑定到 80 端口。

为了解决这个问题，可以使用 `proxy` 命令生成代理。例如，可以将来自 `http://elasticsearch.test` 的所有流量代理到 `http://127.0.0.1:9200`：

```shell
# 通过 HTTP 代理...
valet proxy elasticsearch http://127.0.0.1:9200

# 通过 TLS + HTTP/2 代理...
valet proxy elasticsearch http://127.0.0.1:9200 --secure
```

可以使用 `unproxy` 命令移除代理：

```shell
valet unproxy elasticsearch
```

可以使用 `proxies` 命令列出所有已代理的站点配置：

```shell
valet proxies
```

<a name="custom-valet-drivers"></a>
## 自定义 Valet 驱动

你可以编写自己的 Valet「驱动」，为在 Valet 未原生支持的框架或 CMS 上运行的 PHP 应用提供服务。安装 Valet 时，系统会创建 `~/.config/valet/Drivers` 目录，其中包含 `SampleValetDriver.php` 文件。该文件包含一个驱动示例，用于演示如何编写自定义驱动。编写驱动只需实现三个方法：`serves`、`isStaticFile` 和 `frontControllerPath`。

这三个方法都接收 `$sitePath`、`$siteName` 和 `$uri` 值作为参数。`$sitePath` 是机器上所提供站点的完全限定路径，例如 `/Users/Lisa/Sites/my-project`。`$siteName` 是域名的「主机名 / 站点名」部分（`my-project`）。`$uri` 是传入请求的 URI（`/foo/bar`）。

完成自定义 Valet 驱动后，请按照 `FrameworkValetDriver.php` 命名约定将其放入 `~/.config/valet/Drivers` 目录。例如，如果你正在为 WordPress 编写自定义 Valet 驱动，文件名应为 `WordPressValetDriver.php`。

下面来看一下自定义 Valet 驱动应实现的各个方法的示例。

<a name="the-serves-method"></a>
#### `serves` 方法

如果驱动应处理传入的请求，`serves` 方法应返回 `true`；否则应返回 `false`。因此，在此方法中，应尝试判断给定的 `$sitePath` 是否包含你要提供服务的项目类型。

例如，假设我们正在编写 `WordPressValetDriver`，其 `serves` 方法可能如下所示：

```php
/**
 * 判断该驱动是否为请求提供服务。
 */
public function serves(string $sitePath, string $siteName, string $uri): bool
{
    return is_dir($sitePath.'/wp-admin');
}
```

<a name="the-isstaticfile-method"></a>
#### `isStaticFile` 方法

`isStaticFile` 方法应判断传入的请求是否针对图片或样式表等「静态」文件。如果请求的是静态文件，该方法应返回静态文件在磁盘上的完全限定路径。如果传入的请求不是针对静态文件，该方法应返回 `false`：

```php
/**
 * 判断传入的请求是否针对静态文件。
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

> [!WARNING]
> 只有当 `serves` 方法对传入的请求返回 `true`，且请求 URI 不是 `/` 时，才会调用 `isStaticFile` 方法。

<a name="the-frontcontrollerpath-method"></a>
#### `frontControllerPath` 方法

`frontControllerPath` 方法应返回应用「前端控制器」的完全限定路径，该控制器通常是 `index.php` 文件或等效文件：

```php
/**
 * 获取应用前端控制器的完整解析路径。
 */
public function frontControllerPath(string $sitePath, string $siteName, string $uri): string
{
    return $sitePath.'/public/index.php';
}
```

<a name="local-drivers"></a>
### 本地驱动

如果只想为单个应用定义自定义 Valet 驱动，请在应用根目录中创建 `LocalValetDriver.php` 文件。自定义驱动可以继承基础 `ValetDriver` 类，也可以继承现有的特定应用驱动，例如 `LaravelValetDriver`：

```php
use Valet\Drivers\LaravelValetDriver;

class LocalValetDriver extends LaravelValetDriver
{
    /**
     * 判断该驱动是否为请求提供服务。
     */
    public function serves(string $sitePath, string $siteName, string $uri): bool
    {
        return true;
    }

    /**
     * 获取应用前端控制器的完整解析路径。
     */
    public function frontControllerPath(string $sitePath, string $siteName, string $uri): string
    {
        return $sitePath.'/public_html/index.php';
    }
}
```

<a name="other-valet-commands"></a>
## 其他 Valet 命令

<div class="overflow-auto">

| 命令 | 描述 |
| --- | --- |
| `valet list` | 显示所有 Valet 命令的列表。 |
| `valet diagnose` | 输出诊断信息，以帮助调试 Valet。 |
| `valet directory-listing` | 确定目录列表行为。默认值为「off」，即为目录渲染 404 页面。 |
| `valet forget` | 在「停放」目录中运行此命令，将其从停放目录列表中移除。 |
| `valet log` | 查看 Valet 服务写入的日志列表。 |
| `valet paths` | 查看所有「停放」路径。 |
| `valet restart` | 重启 Valet 守护进程。 |
| `valet start` | 启动 Valet 守护进程。 |
| `valet stop` | 停止 Valet 守护进程。 |
| `valet trust` | 为 Brew 和 Valet 添加 sudoers 文件，使 Valet 命令可以在不提示输入密码的情况下运行。 |
| `valet uninstall` | 卸载 Valet：显示手动卸载说明。传入 `--force` 选项可强制删除 Valet 的所有资源。 |

</div>

<a name="valet-directories-and-files"></a>
## Valet 目录与文件

排查 Valet 环境问题时，以下目录和文件信息可能会有所帮助：

#### `~/.config/valet`

包含 Valet 的所有配置。你可能需要备份此目录。

#### `~/.config/valet/dnsmasq.d/`

此目录包含 DNSMasq 的配置。

#### `~/.config/valet/Drivers/`

此目录包含 Valet 的驱动。驱动决定了如何为特定框架 / CMS 提供服务。

#### `~/.config/valet/Nginx/`

此目录包含 Valet 的所有 Nginx 站点配置。运行 `install` 和 `secure` 命令时会重新生成这些文件。

#### `~/.config/valet/Sites/`

此目录包含所有[已链接项目](#the-link-command)的符号链接。

#### `~/.config/valet/config.json`

此文件是 Valet 的主配置文件。

#### `~/.config/valet/valet.sock`

此文件是 Valet 的 Nginx 安装所使用的 PHP-FPM 套接字。只有在 PHP 正常运行时，此文件才会存在。

#### `~/.config/valet/Log/fpm-php.www.log`

此文件是用户级 PHP 错误日志。

#### `~/.config/valet/Log/nginx-error.log`

此文件是用户级 Nginx 错误日志。

#### `/usr/local/var/log/php-fpm.log`

此文件是系统级 PHP-FPM 错误日志。

#### `/usr/local/var/log/nginx`

此目录包含 Nginx 访问日志和错误日志。

#### `/usr/local/etc/php/X.X/conf.d`

此目录包含用于各种 PHP 配置设置的 `*.ini` 文件。

#### `/usr/local/etc/php/X.X/php-fpm.d/valet-fpm.conf`

此文件是 PHP-FPM 进程池的配置文件。

#### `~/.composer/vendor/laravel/valet/cli/stubs/secure.valet.conf`

此文件是用于为站点生成 SSL 证书的默认 Nginx 配置。

<a name="disk-access"></a>
### 磁盘访问权限

自 macOS 10.14 起，[系统默认会限制对某些文件和目录的访问](https://manuals.info.apple.com/MANUALS/1000/MA1902/en_US/apple-platform-security-guide.pdf)。这些限制包括「桌面」、「文稿」和「下载」目录。此外，对网络卷和可移动卷的访问也受到限制。因此，Valet 建议将站点文件夹放在这些受保护的位置之外。

但是，如果要从其中一个位置提供站点服务，则需要授予 Nginx「完全磁盘访问权限」。否则，Nginx 可能会出现服务器错误或其他不可预测的行为，尤其是在提供静态资源时。通常，macOS 会自动提示你授予 Nginx 对这些位置的完全访问权限。你也可以通过「系统偏好设置」>「安全性与隐私」>「隐私」，然后选择「完全磁盘访问权限」来手动设置。接下来，在主窗口面板中启用所有 `nginx` 条目。
