
# Laravel Dusk

- [介绍](#introduction)
- [安装](#installation)
  - [管理 ChromeDriver 安装](#managing-chromedriver-installations)
  - [使用其他浏览器](#using-other-browsers)
- [开始使用](#getting-started)
  - [生成测试](#generating-tests)
  - [在每次测试后重置数据库](#resetting-the-database-after-each-test)
  - [运行测试](#running-tests)
  - [环境处理](#environment-handling)
- [浏览器基础](#browser-basics)
  - [创建浏览器](#creating-browsers)
  - [导航](#navigation)
  - [调整浏览器窗口大小](#resizing-browser-windows)
  - [浏览器宏](#browser-macros)
  - [身份验证](#authentication)
  - [Cookies](#cookies)
  - [执行 JavaScript](#executing-javascript)
  - [截取屏幕截图](#taking-a-screenshot)
  - [将控制台输出存储到磁盘](#storing-console-output-to-disk)
  - [将页面源代码存储到磁盘](#storing-page-source-to-disk)
- [与元素交互](#interacting-with-elements)
  - [Dusk 选择器](#dusk-selectors)
  - [文本、值和属性](#text-values-and-attributes)
  - [与表单交互](#interacting-with-forms)
  - [附加文件](#attaching-files)
  - [按下按钮](#pressing-buttons)
  - [点击链接](#clicking-links)
  - [使用键盘](#using-the-keyboard)
  - [使用鼠标](#using-the-mouse)
  - [JavaScript 对话框](#javascript-dialogs)
  - [与内联框架交互](#interacting-with-iframes)
  - [限制选择器作用域](#scoping-selectors)
  - [等待元素](#waiting-for-elements)
  - [将元素滚动到视图中](#scrolling-an-element-into-view)
- [可用的断言](#available-assertions)
- [页面](#pages)
  - [生成页面](#generating-pages)
  - [配置页面](#configuring-pages)
  - [导航到页面](#navigating-to-pages)
  - [简写选择器](#shorthand-selectors)
  - [页面方法](#page-methods)
- [组件](#components)
  - [生成组件](#generating-components)
  - [使用组件](#using-components)
- [持续集成](#continuous-integration)
  - [Heroku CI](#running-tests-on-heroku-ci)
  - [Travis CI](#running-tests-on-travis-ci)
  - [GitHub Actions](#running-tests-on-github-actions)
  - [Chipper CI](#running-tests-on-chipper-ci)


## 引言

[Laravel Dusk](https://github.com/laravel/dusk) 提供了一个富有表现力且易于使用的浏览器自动化和测试 API。默认情况下，Dusk 不要求你在本地计算机上安装 JDK 或 Selenium。相反，Dusk 使用一个独立的 [ChromeDriver](https://sites.google.com/chromium.org/driver) 安装。不过，你也可以自由地使用任何其他与 Selenium 兼容的驱动程序。



## 安装

首先，你需要安装 [Google Chrome](https://www.google.com/chrome)，并在你的项目中添加 `laravel/dusk` 的 Composer 依赖：

```shell
composer require laravel/dusk --dev
```

> [!警告]
> 如果你是手动注册 Dusk 的服务提供者，那么绝对不要在生产环境中注册它，因为这样做可能会导致任意用户能够通过 Dusk 直接认证进入你的应用。

安装完 Dusk 包后，执行 `dusk:install` Artisan 命令。
`dusk:install` 命令会创建一个 `tests/Browser` 目录、一个示例 Dusk 测试文件，并为你的操作系统安装 Chrome Driver 二进制文件：

```shell
php artisan dusk:install
```

接下来，在应用的 `.env` 文件中设置 `APP_URL` 环境变量。这个值应与您在浏览器中访问应用时使用的 URL 相匹配。

> 如果你使用 [Laravel Sail](/docs/laravel/12.x/sail) 来管理本地开发环境，请参考 Sail 文档中关于 [配置和运行 Dusk 测试](/docs/laravel/12.x/sail#laravel-dusk) 的内容。

### 管理 ChromeDriver 安装
如果你想安装不同版本的 ChromeDriver（而不是通过 `dusk:install` 命令安装的默认版本），可以使用 `dusk:chrome-driver` 命令：

```shell
# 安装适用于当前操作系统的最新版 ChromeDriver...
php artisan dusk:chrome-driver

# 安装指定版本的 ChromeDriver（当前操作系统）...
php artisan dusk:chrome-driver 86

# 为所有支持的操作系统安装指定版本的 ChromeDriver...
php artisan dusk:chrome-driver --all

# 安装与检测到的 Chrome / Chromium 版本匹配的 ChromeDriver（当前操作系统）...
php artisan dusk:chrome-driver --detect
```

> [!警告]
> Dusk 需要 `chromedriver` 二进制文件具有可执行权限。
如果运行 Dusk 时遇到问题，请使用以下命令确保它们可执行：`chmod -R 0755 vendor/laravel/dusk/bin/`



### 使用其他浏览器

默认情况下，Dusk 使用 Google Chrome 和一个独立的 [ChromeDriver](https://sites.google.com/chromium.org/driver) 安装来运行你的浏览器测试。但是，你可以启动你自己的 Selenium 服务器，并且让测试在任何你想要的浏览器上运行。

开始之前，打开你的 `tests/DuskTestCase.php` 文件，这是你应用的 Dusk 测试基类。在这个文件中，你可以移除对 `startChromeDriver` 方法的调用。这样会阻止 Dusk 自动启动 ChromeDriver：

```php
/**
 * 为 Dusk 测试执行做准备。
 *
 * @beforeClass
 */
public static function prepare(): void
{
    // static::startChromeDriver();
}
```

接下来，你可以修改 `driver` 方法以连接到你选择的 URL 和端口。此外，你可以修改应传递给 WebDriver 的“期望能力”：

```php
use Facebook\WebDriver\Remote\RemoteWebDriver;

/**
 * 创建 RemoteWebDriver 实例。
 */
protected function driver(): RemoteWebDriver
{
    return RemoteWebDriver::create(
        'http://localhost:4444/wd/hub', DesiredCapabilities::phantomjs()
    );
}
```

## 快速开始

### 生成测试

使用 `dusk:make` Artisan 命令生成一个 Dusk 测试。生成的测试将被放置在 `tests/Browser` 目录中：

```shell
php artisan dusk:make LoginTest
```

### 每个测试后重置数据库

你写的大多数测试会与从你的应用数据库获取数据的页面交互；但是，你的 Dusk 测试不应使用 `RefreshDatabase` trait。
`RefreshDatabase` trait 利用数据库事务，而这些事务无法跨 HTTP 请求使用。你有两个选择：`DatabaseMigrations` trait 和 `DatabaseTruncation` trait。



#### 使用数据库迁移

`DatabaseMigrations` 特性将在每个测试之前运行数据库迁移。然而，每次测试都删除并重新创建数据库表通常比截断表的速度要慢：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;

uses(DatabaseMigrations::class);

//
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    use DatabaseMigrations;

    //
}
```

> [!警告]
> 在执行 Dusk 测试时，不能使用 SQLite 的内存数据库。由于浏览器在其自身进程中执行，无法访问其他进程中的内存数据库。

#### 使用数据库截断

`DatabaseTruncation` 特性将在第一个测试中运行数据库迁移，确保数据库表已经正确创建。但在随后的测试中，数据库表只会被截断（truncate），这比重新运行所有数据库迁移更快：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\DatabaseTruncation;
use Laravel\Dusk\Browser;

uses(DatabaseTruncation::class);

//
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseTruncation;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    use DatabaseTruncation;

    //
}
```
默认情况下，该特性会截断除 `migrations` 表之外的所有表。如果你想自定义需要截断的表，可以在测试类中定义 `$tablesToTruncate` 属性：

> [!注意]
> 如果你使用 Pest，应该在基础的 `DuskTestCase` 类或测试文件继承的任何类上定义这些属性或方法。

```php
/**
 * 指定哪些表应该被截断。
 *
 * @var array
 */
protected $tablesToTruncate = ['users'];
```



或者，你可以在测试类中定义一个 `$exceptTables` 属性来指定哪些表应排除在截断之外：

```php
/**
 * 指定哪些表应排除在截断之外。
 *
 * @var array
 */
protected $exceptTables = ['users'];
```

你也可以定义一个 `$connectionsToTruncate` 属性来指定哪些数据库连接的表应该被截断：

```php
/**
 * 指定哪些数据库连接的表应被截断。
 *
 * @var array
 */
protected $connectionsToTruncate = ['mysql'];
```

如果你想在数据库截断之前或之后执行代码，可以在测试类中定义 `beforeTruncatingDatabase` 或 `afterTruncatingDatabase` 方法：

```php
/**
 * 在数据库开始截断之前执行的操作。
 */
protected function beforeTruncatingDatabase(): void
{
    //
}

/**
 * 在数据库截断完成之后执行的操作。
 */
protected function afterTruncatingDatabase(): void
{
    //
}
```

### 运行测试

运行浏览器测试，请执行 `dusk` Artisan 命令：

```shell
php artisan dusk
```

如果你上次运行 `dusk` 命令时有测试失败，可以先使用 `dusk:fails` 命令重新运行失败的测试，节省时间：

```shell
php artisan dusk:fails
```

`dusk` 命令接受 Pest / PHPUnit 测试运行器通常接受的任何参数，例如，你可以只运行某个 [分组](https://docs.phpunit.de/en/10.5/annotations.html#group)的测试：

```shell
php artisan dusk --group=foo
```

> [!注意]
> 如果你使用 [Laravel Sail](/docs/laravel/12.x/sail) 管理本地开发环境，请参考 Sail 文档中关于 [配置和运行 Dusk 测试](/docs/laravel/12.x/sail#laravel-dusk) 的说明。



#### 手动启动 ChromeDriver

默认情况下，Dusk 会自动尝试启动 ChromeDriver。如果这在你的系统上不起作用，你可以在运行 `dusk` 命令之前手动启动 ChromeDriver。如果选择手动启动 ChromeDriver，你应该注释掉 `tests/DuskTestCase.php` 文件中的以下代码：

```php
/**
 * 为 Dusk 测试执行做准备。
 *
 * @beforeClass
 */
public static function prepare(): void
{
    // static::startChromeDriver();
}
```

此外，如果你在除 9515 以外的端口启动 ChromeDriver，你需要修改同一文件中的 `driver` 方法，反映正确的端口：

```php
use Facebook\WebDriver\Remote\RemoteWebDriver;

/**
 * 创建 RemoteWebDriver 实例。
 */
protected function driver(): RemoteWebDriver
{
    return RemoteWebDriver::create(
        'http://localhost:9515', DesiredCapabilities::chrome()
    );
}
```

### 环境处理

为了强制 Dusk 在运行测试时使用其专用的环境文件，你可以在项目根目录下创建 `.env.dusk.{environment}` 文件。例如，如果你从 `local` 环境启动 `dusk` 命令，则应创建 `.env.dusk.local` 文件。

运行测试时，Dusk 会备份你的 `.env` 文件，并将你的 Dusk 环境文件重命名为 `.env`。测试完成后，`.env` 文件会被恢复。

## 浏览器基础

### 创建浏览器

开始时，我们写一个测试，验证能否登录到应用。生成测试后，可以修改它，导航到登录页，输入凭证并点击“登录”按钮。要创建浏览器实例，可以在 Dusk 测试中调用 `browse` 方法：

```php tab=Pest
<?php

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;

uses(DatabaseMigrations::class);

test('basic example', function () {
    $user = User::factory()->create([
        'email' => 'taylor@laravel.com',
    ]);

    $this->browse(function (Browser $browser) use ($user) {
        $browser->visit('/login')
            ->type('email', $user->email)
            ->type('password', 'password')
            ->press('Login')
            ->assertPathIs('/home');
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    use DatabaseMigrations;

    /**
     * 一个基础的浏览器测试示例。
     */
    public function test_basic_example(): void
    {
        $user = User::factory()->create([
            'email' => 'taylor@laravel.com',
        ]);

        $this->browse(function (Browser $browser) use ($user) {
            $browser->visit('/login')
                ->type('email', $user->email)
                ->type('password', 'password')
                ->press('Login')
                ->assertPathIs('/home');
        });
    }
}
```



如上例所示，`browse` 方法接受一个闭包。Dusk 会自动传入一个浏览器实例给这个闭包，该实例是与应用交互和进行断言的主要对象。

#### 创建多个浏览器

有时候为了完整测试，可能需要多个浏览器实例。例如，测试一个通过 websocket 交互的聊天界面时，就需要多个浏览器。要创建多个浏览器，只需在传递给 `browse` 方法的闭包参数中增加更多浏览器实例：

```php
$this->browse(function (Browser $first, Browser $second) {
    $first->loginAs(User::find(1))
        ->visit('/home')
        ->waitForText('Message');

    $second->loginAs(User::find(2))
        ->visit('/home')
        ->waitForText('Message')
        ->type('message', 'Hey Taylor')
        ->press('Send');

    $first->waitForText('Hey Taylor')
        ->assertSee('Jeffrey Way');
});
```

### 导航

`visit` 方法可用于访问应用中的指定 URI：

```php
$browser->visit('/login');
```

你也可以用 `visitRoute` 方法访问一个[命名路由](/docs/laravel/12.x/routing#named-routes)：

```php
$browser->visitRoute($routeName, $parameters);
```

通过 `back` 和 `forward` 方法可以向“后退”和“前进”导航：

```php
$browser->back();

$browser->forward();
```

`refresh` 方法用来刷新当前页面：

```php
$browser->refresh();
```

### 调整浏览器窗口大小

使用 `resize` 方法可以调整浏览器窗口大小：

```php
$browser->resize(1920, 1080);
```

`maximize` 方法用于最大化浏览器窗口：

```php
$browser->maximize();
```



`fitContent` 方法会将浏览器窗口大小调整为其内容的大小：

```php
$browser->fitContent();
```

当测试失败时，Dusk 会自动调整浏览器窗口大小以适应内容，然后再截图。你可以通过调用 `disableFitOnFailure` 方法关闭此功能：

```php
$browser->disableFitOnFailure();
```

你还可以使用 `move` 方法将浏览器窗口移动到屏幕上的其他位置：

```php
$browser->move($x = 100, $y = 100);
```

### 浏览器宏（Browser Macros）

如果你想定义一个自定义的浏览器方法，以便在多个测试中复用，可以使用 `Browser` 类的 `macro` 方法。通常应在[服务提供者](/docs/laravel/12.x/providers)的 `boot` 方法中调用：

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Laravel\Dusk\Browser;

class DuskServiceProvider extends ServiceProvider
{
    /**
     * 注册 Dusk 浏览器宏。
     */
    public function boot(): void
    {
        Browser::macro('scrollToElement', function (string $element = null) {
            $this->script("$('html, body').animate({ scrollTop: $('$element').offset().top }, 0);");

            return $this;
        });
    }
}
```
`macro` 方法第一个参数是宏名称，第二个参数是闭包。当你在 `Browser` 实例上调用宏时，这个闭包会被执行：

```php
$this->browse(function (Browser $browser) use ($user) {
    $browser->visit('/pay')
        ->scrollToElement('#credit-card-details')
        ->assertSee('Enter Credit Card Details');
});
```

### 认证

在测试需要认证的页面时，可以使用 Dusk 的 `loginAs` 方法，避免每次测试都操作登录页面。`loginAs` 方法接收用户模型的主键或模型实例：

```php
use App\Models\User;
use Laravel\Dusk\Browser;

$this->browse(function (Browser $browser) {
    $browser->loginAs(User::find(1))
        ->visit('/home');
});
```

> [!警告]
> 使用 `loginAs` 方法后，该用户会话会在当前测试文件的所有测试中保持有效。


### Cookies

你可以使用 `cookie` 方法来获取或设置一个加密的 cookie 值。默认情况下，Laravel 创建的所有 cookie 都是加密的：

```php
$browser->cookie('name');

$browser->cookie('name', 'Taylor');
```

你也可以使用 `plainCookie` 方法来获取或设置未加密的 cookie 值：

```php
$browser->plainCookie('name');

$browser->plainCookie('name', 'Taylor');
```

使用 `deleteCookie` 方法可以删除指定的 cookie：

```php
$browser->deleteCookie('name');
```

### 执行 JavaScript

你可以使用 `script` 方法在浏览器内执行任意的 JavaScript 代码：

```php
$browser->script('document.documentElement.scrollTop = 0');

$browser->script([
    'document.body.scrollTop = 0',
    'document.documentElement.scrollTop = 0',
]);

$output = $browser->script('return window.location.pathname');
```

### 截图

使用 `screenshot` 方法可以截取当前页面的截图，并以指定文件名保存，所有截图会保存在 `tests/Browser/screenshots` 目录下：

```php
$browser->screenshot('filename');
```

`responsiveScreenshots` 方法可以在不同屏幕宽度断点下自动截取一系列截图：

```php
$browser->responsiveScreenshots('filename');
```

`screenshotElement` 方法可以截取页面中特定元素的截图：

```php
$browser->screenshotElement('#selector', 'filename');
```

### 保存控制台输出到磁盘

使用 `storeConsoleLog` 方法将当前浏览器的控制台日志保存到磁盘，日志会保存在 `tests/Browser/console` 目录下：

```php
$browser->storeConsoleLog('filename');
```

### 保存页面源码到磁盘



你可以使用 `storeSource` 方法将当前页面的源代码写入磁盘，并使用给定的文件名保存。页面源代码将被存储在 `tests/Browser/source` 目录中：

```php
$browser->storeSource('filename');
```

## 与元素交互

### Dusk 选择器

为元素交互选择合适的 CSS 选择器，是编写 Dusk 测试中最困难的部分之一。随着时间推移，前端的变动可能会导致类似下面这样的 CSS 选择器破坏你的测试：

```html
// HTML...

<button>Login</button>
```

```php
// Test...

$browser->click('.login-page .container div > button');
```

Dusk 选择器允许你专注于编写高效的测试，而不是记住复杂的 CSS 选择器。要定义一个选择器，只需在 HTML 元素中添加一个 `dusk` 属性。然后，在与 Dusk 浏览器交互时，使用 `@` 前缀选择器，就可以在测试中操作对应的元素：

html

复制编辑

```html
// HTML...

<button dusk="login-button">Login</button>
```

```php
// Test...

$browser->click('@login-button');
```

如果需要，你可以通过 `selectorHtmlAttribute` 方法自定义 Dusk 选择器所使用的 HTML 属性。通常，这个方法应在应用的 `AppServiceProvider` 的 `boot` 方法中调用：


```php
use Laravel\Dusk\Dusk;

Dusk::selectorHtmlAttribute('data-dusk');
```

### 文本、值与属性

#### 获取和设置值

Dusk 提供了多种方法来与页面元素的当前值、显示文本和属性进行交互。
例如，要获取匹配指定 CSS 或 Dusk 选择器的元素的 “值”，可以使用 `value` 方法：

```php
// 获取值...
$value = $browser->value('selector');

// 设置值...
$browser->value('selector', 'value');
```



你可以使用 `inputValue` 方法来获取具有指定字段名的输入元素的 “值”：

```php
$value = $browser->inputValue('field');
```

#### 获取文本

`text` 方法可用于获取与给定选择器匹配的元素的显示文本：

```php
$text = $browser->text('selector');
```

#### 获取属性

最后，`attribute` 方法可用于获取与给定选择器匹配的元素的某个属性的值：

```php
$attribute = $browser->attribute('selector', 'value');
```

### 与表单交互

#### 输入值

Dusk 提供了多种方法与表单和输入元素进行交互。首先，让我们看一个在输入字段中输入文本的例子：

```php
$browser->type('email', 'taylor@laravel.com');
```

注意，虽然在必要时该方法可以接受一个 CSS 选择器，但我们并不一定需要将 CSS 选择器传入 `type` 方法。
如果没有提供 CSS 选择器，Dusk 会查找具有给定 `name` 属性的 `input` 或 `textarea` 字段。

若要在不清空字段内容的情况下追加文本，可以使用 `append` 方法：

```php
$browser->type('tags', 'foo')
    ->append('tags', ', bar, baz');
```

你可以使用 `clear` 方法清空输入框的值：

```php
$browser->clear('email');
```

你可以使用 `typeSlowly` 方法让 Dusk 慢速输入。默认情况下，Dusk 在每次按键之间会暂停 100 毫秒。
若要自定义按键之间的时间，可以将所需的毫秒数作为该方法的第三个参数传入：

```php
$browser->typeSlowly('mobile', '+1 (202) 555-5555');

$browser->typeSlowly('mobile', '+1 (202) 555-5555', 300);
```



你可以使用 `appendSlowly` 方法来慢速追加文本：

```php
$browser->type('tags', 'foo')
    ->appendSlowly('tags', ', bar, baz');
```

#### 下拉框

要选择 `select` 元素中的某个选项，可以使用 `select` 方法。与 `type` 方法类似，`select` 方法不需要完整的 CSS 选择器。
在向 `select` 方法传递值时，应传递选项的实际值（`value` 属性），而不是显示文本：

```php
$browser->select('size', 'Large');
```

如果省略第二个参数，则会随机选择一个选项：

```php
$browser->select('size');
```

如果将数组作为第二个参数传递给 `select` 方法，可以一次选择多个选项：

```php
$browser->select('categories', ['Art', 'Music']);
```

#### 复选框

要“勾选”复选框输入，可以使用 `check` 方法。与许多其他输入相关方法一样，不需要完整的 CSS 选择器。
如果找不到 CSS 选择器匹配，Dusk 会查找 `name` 属性匹配的复选框：

```php
$browser->check('terms');
```

要“取消勾选”复选框输入，可以使用 `uncheck` 方法：

```php
$browser->uncheck('terms');
```

#### 单选按钮

要“选择”某个 `radio` 输入选项，可以使用 `radio` 方法。与其他输入相关方法类似，不需要完整的 CSS 选择器。
如果找不到 CSS 选择器匹配，Dusk 会查找 `name` 和 `value` 属性匹配的 `radio` 输入：

```php
$browser->radio('size', 'large');
```

### 附加文件



`attach` 方法可用于将文件附加到 `file` 类型的输入元素上。和许多其他与输入相关的方法一样，它不需要完整的 CSS 选择器。
如果找不到 CSS 选择器匹配，Dusk 会查找 `name` 属性匹配的 `file` 输入元素：

```php
$browser->attach('photo', __DIR__.'/photos/mountains.png');
```

> [!警告]
> `attach` 功能需要服务器安装并启用 PHP 的 `Zip` 扩展。

### 按下按钮

`press` 方法可用于点击页面上的按钮元素。传递给 `press` 方法的参数可以是按钮的显示文本，或 CSS / Dusk 选择器：

```php
$browser->press('Login');
```

在提交表单时，很多应用会在按钮被点击后将其禁用，并在表单提交的 HTTP 请求完成后重新启用。
要点击按钮并等待它重新启用，可以使用 `pressAndWaitFor` 方法：

```php
// 点击按钮并等待最多 5 秒重新启用...
$browser->pressAndWaitFor('Save');

// 点击按钮并等待最多 1 秒重新启用...
$browser->pressAndWaitFor('Save', 1);
```

### 点击链接

要点击链接，可以在浏览器实例上使用 `clickLink` 方法。
`clickLink` 方法会点击具有指定显示文本的链接：

```php
$browser->clickLink($linkText);
```

要判断页面上是否可见指定显示文本的链接，可以使用 `seeLink` 方法：

```php
if ($browser->seeLink($linkText)) {
    // ...
}
```

> [!警告]
> 这些方法依赖 jQuery，如果页面上没有 jQuery，Dusk 会自动将其注入页面，以保证测试期间可用。



### 使用键盘

`keys` 方法允许你向指定元素发送比 `type` 方法更复杂的输入序列。例如，你可以让 Dusk 在输入值时按住修饰键。
在下面的示例中，在输入 `taylor` 时会按住 `shift` 键，输入完成后，再输入 `swift` 时则不使用任何修饰键：

```php
$browser->keys('selector', ['{shift}', 'taylor'], 'swift');
```

另一个常见用例是向应用的主 CSS 选择器发送“键盘快捷键”组合：

```php
$browser->keys('.app', ['{command}', 'j']);
```

> [!笔记]
> 所有修饰键（例如 `{command}`）都用 `{}` 包裹，并且对应于 `Facebook\WebDriver\WebDriverKeys` 类中定义的常量，该类可以在 [GitHub 上查看](https://github.com/php-webdriver/php-webdriver/blob/master/lib/WebDriverKeys.php)。

#### 流式键盘交互

Dusk 还提供了 `withKeyboard` 方法，可以通过 `Laravel\Dusk\Keyboard` 类以流式方式执行复杂的键盘交互。
`Keyboard` 类提供了 `press`、`release`、`type` 和 `pause` 方法：

```php
use Laravel\Dusk\Keyboard;

$browser->withKeyboard(function (Keyboard $keyboard) {
    $keyboard->press('c')
        ->pause(1000)
        ->release('c')
        ->type(['c', 'e', 'o']);
});
```

#### 键盘宏

如果你想定义可在整个测试套件中轻松复用的自定义键盘交互，可以使用 `Keyboard` 类提供的 `macro` 方法。
通常，你应该在 [服务提供器](/docs/laravel/12.x/providers) 的 `boot` 方法中调用此方法：

```php
<?php

namespace App\Providers;

use Facebook\WebDriver\WebDriverKeys;
use Illuminate\Support\ServiceProvider;
use Laravel\Dusk\Keyboard;
use Laravel\Dusk\OperatingSystem;

class DuskServiceProvider extends ServiceProvider
{
    /**
     * 注册 Dusk 的浏览器宏
     */
    public function boot(): void
    {
        Keyboard::macro('copy', function (string $element = null) {
            $this->type([
                OperatingSystem::onMac() ? WebDriverKeys::META : WebDriverKeys::CONTROL, 'c',
            ]);

            return $this;
        });

        Keyboard::macro('paste', function (string $element = null) {
            $this->type([
                OperatingSystem::onMac() ? WebDriverKeys::META : WebDriverKeys::CONTROL, 'v',
            ]);

            return $this;
        });
    }
}
```



`macro` 函数的第一个参数是宏的名称，第二个参数是一个闭包。
当在 `Keyboard` 实例上调用该宏方法时，这个闭包就会被执行：

```php
$browser->click('@textarea')
    ->withKeyboard(fn (Keyboard $keyboard) => $keyboard->copy())
    ->click('@another-textarea')
    ->withKeyboard(fn (Keyboard $keyboard) => $keyboard->paste());
```

### 使用鼠标

#### 点击元素

`click` 方法可用于点击符合给定 CSS 选择器或 Dusk 选择器的元素：

```php
$browser->click('.selector');
```

`clickAtXPath` 方法可用于点击符合给定 XPath 表达式的元素：

```php
$browser->clickAtXPath('//div[@class = "selector"]');
```

`clickAtPoint` 方法可用于点击浏览器可视区域内指定坐标处的最上层元素（坐标是相对视口的）：

```php
$browser->clickAtPoint($x = 0, $y = 0);
```

`doubleClick` 方法可用于模拟鼠标双击：

```php
$browser->doubleClick();

$browser->doubleClick('.selector');
```

`rightClick` 方法可用于模拟鼠标右键点击：

```php
$browser->rightClick();

$browser->rightClick('.selector');
```

`clickAndHold` 方法可用于模拟鼠标按键按下并保持不放。
随后调用 `releaseMouse` 方法可以释放鼠标按键：

```php
$browser->clickAndHold('.selector');

$browser->clickAndHold()
    ->pause(1000)
    ->releaseMouse();
```

`controlClick` 方法可用于在浏览器中模拟 `ctrl+click` 操作：

```php
$browser->controlClick();

$browser->controlClick('.selector');
```



#### 鼠标悬停

`mouseover` 方法用于将鼠标移动到符合给定 CSS 或 Dusk 选择器的元素上：

```php
$browser->mouseover('.selector');
```

#### 拖拽操作

`drag` 方法用于将一个元素从指定选择器位置拖拽到另一个元素位置：

```php
$browser->drag('.from-selector', '.to-selector');
```

也可以只在一个方向上拖动元素：

```php
$browser->dragLeft('.selector', $pixels = 10);
$browser->dragRight('.selector', $pixels = 10);
$browser->dragUp('.selector', $pixels = 10);
$browser->dragDown('.selector', $pixels = 10);
```

还可以按照偏移量来拖拽元素：

```php
$browser->dragOffset('.selector', $x = 10, $y = 10);
```

### JavaScript 对话框

Dusk 提供了多种方法与 JavaScript 对话框交互。
例如，可以使用 `waitForDialog` 等待对话框出现（可选参数是等待的秒数）：

```php
$browser->waitForDialog($seconds = null);
```

`assertDialogOpened` 用于断言某个对话框已显示，并且包含指定的消息内容：

```php
$browser->assertDialogOpened('Dialog message');
```

如果对话框是 `prompt` 类型，可以用 `typeInDialog` 在输入框中输入内容：

```php
$browser->typeInDialog('Hello World');
```

要点击“确定”按钮关闭对话框，可使用 `acceptDialog`：

```php
$browser->acceptDialog();
```

要点击“取消”按钮关闭对话框，可使用 `dismissDialog`：

```php
$browser->dismissDialog();
```



### 与内嵌框架 (iframe) 交互

如果需要操作 iframe 内的元素，可以使用 `withinFrame` 方法。传入的闭包中所有对元素的操作都会限定在指定的 iframe 上下文中：

```php
$browser->withinFrame('#credit-card-details', function ($browser) {
    $browser->type('input[name="cardnumber"]', '4242424242424242')
        ->type('input[name="exp-date"]', '1224')
        ->type('input[name="cvc"]', '123')
        ->press('Pay');
});
```

### 作用域选择器

有时你可能想在某个选择器限定的范围内执行多次操作。比如，只在某个表格内确认存在某段文字，然后点击该表格中的按钮。可以用 `with` 方法实现，这个方法中闭包内的所有操作都会被限定在原始选择器内：

```php
$browser->with('.table', function (Browser $table) {
    $table->assertSee('Hello World')
        ->clickLink('Delete');
});
```

有时你可能想跳出当前作用域去执行断言，可以使用 `elsewhere` 和 `elsewhereWhenAvailable` 方法：

```php
$browser->with('.table', function (Browser $table) {
    // 当前作用域是 `body .table`...

    $browser->elsewhere('.page-title', function (Browser $title) {
        // 当前作用域是 `body .page-title`...
        $title->assertSee('Hello World');
    });

    $browser->elsewhereWhenAvailable('.page-title', function (Browser $title) {
        // 当前作用域是 `body .page-title`...
        $title->assertSee('Hello World');
    });
});
```

### 等待元素

在测试大量使用 JavaScript 的应用时，常常需要等待某些元素或数据出现后再继续测试。Dusk 提供了多种方法，允许你等待元素变为可见，或者等待某个 JavaScript 表达式结果变为 `true`，让测试变得简单方便。



#### 等待

如果你只是需要让测试暂停指定的毫秒数，可以使用 `pause` 方法：

```php
$browser->pause(1000);
```

如果你只想在某个条件为 `true` 时才暂停测试，可以用 `pauseIf` 方法：

```php
$browser->pauseIf(App::environment('production'), 1000);
```

同样，如果你想在某个条件不为 `true` 时暂停测试，可以使用 `pauseUnless` 方法：

```php
$browser->pauseUnless(App::environment('testing'), 1000);
```

#### 等待选择器

`waitFor` 方法用于暂停测试执行，直到页面上显示出匹配给定 CSS 或 Dusk 选择器的元素。默认情况下，它最多等待五秒，超时会抛出异常。如果需要，你可以传入第二个参数自定义超时时间（秒）：

```php
// 最多等待五秒，直到元素出现...
$browser->waitFor('.selector');

// 最多等待一秒，直到元素出现...
$browser->waitFor('.selector', 1);
```

你也可以等待匹配的元素包含指定文本：

```php
// 最多等待五秒，直到元素包含指定文本...
$browser->waitForTextIn('.selector', 'Hello World');

// 最多等待一秒，直到元素包含指定文本...
$browser->waitForTextIn('.selector', 'Hello World', 1);
```

你还可以等待匹配的元素从页面中消失：

```php
// 最多等待五秒，直到元素消失...
$browser->waitUntilMissing('.selector');

// 最多等待一秒，直到元素消失...
$browser->waitUntilMissing('.selector', 1);
```



或者，你可以等待匹配给定选择器的元素被启用或禁用：

```php
// 最多等待五秒，直到选择器被启用...
$browser->waitUntilEnabled('.selector');

// 最多等待一秒，直到选择器被启用...
$browser->waitUntilEnabled('.selector', 1);

// 最多等待五秒，直到选择器被禁用...
$browser->waitUntilDisabled('.selector');

// 最多等待一秒，直到选择器被禁用...
$browser->waitUntilDisabled('.selector', 1);
```

#### 当可用时限定选择器范围

有时，你可能希望等待匹配给定选择器的元素出现，然后与该元素交互。
例如，你可能希望等到一个模态窗口可用，然后在该模态窗口中点击“OK”按钮。
可以使用 `whenAvailable` 方法来实现这一点。
在给定闭包中执行的所有元素操作都会限定在原始选择器范围内：

```php
$browser->whenAvailable('.modal', function (Browser $modal) {
    $modal->assertSee('Hello World')
        ->press('OK');
});
```

#### 等待文本

`waitForText` 方法可用于等待给定文本显示在页面上：

```php
// 最多等待五秒，直到文本出现...
$browser->waitForText('Hello World');

// 最多等待一秒，直到文本出现...
$browser->waitForText('Hello World', 1);
```

你可以使用 `waitUntilMissingText` 方法等待已显示的文本从页面中移除：

```php
// 最多等待五秒，直到文本被移除...
$browser->waitUntilMissingText('Hello World');

// 最多等待一秒，直到文本被移除...
$browser->waitUntilMissingText('Hello World', 1);
```



#### 等待链接

`waitForLink` 方法可用于等待给定链接文本显示在页面上：

```php
// 最多等待五秒，直到链接出现...
$browser->waitForLink('Create');

// 最多等待一秒，直到链接出现...
$browser->waitForLink('Create', 1);
```

#### 等待输入框

`waitForInput` 方法可用于等待给定输入字段在页面上可见：

```php
// 最多等待五秒，直到输入框出现...
$browser->waitForInput($field);

// 最多等待一秒，直到输入框出现...
$browser->waitForInput($field, 1);
```

#### 等待页面位置

当进行路径断言（例如 `$browser->assertPathIs('/home')`）时，如果 `window.location.pathname` 正在异步更新，断言可能会失败。
你可以使用 `waitForLocation` 方法等待位置变为指定值：

```php
$browser->waitForLocation('/secret');
```

`waitForLocation` 方法也可用于等待当前窗口位置变为完整的 URL：

```php
$browser->waitForLocation('https://example.com/path');
```

你还可以等待一个[命名路由](/docs/laravel/12.x/routing#named-routes)的位置：

```php
$browser->waitForRoute($routeName, $parameters);
```

#### 等待页面重新加载

如果你需要在执行某个操作后等待页面重新加载，可以使用 `waitForReload` 方法：

```php
use Laravel\Dusk\Browser;

$browser->waitForReload(function (Browser $browser) {
    $browser->press('Submit');
})
->assertSee('Success!');
```

由于等待页面重新加载的需求通常出现在点击按钮之后，你可以使用 `clickAndWaitForReload` 方法来简化操作：

```php
$browser->clickAndWaitForReload('.selector')
    ->assertSee('something');
```



#### 等待 JavaScript 表达式

有时，你可能希望暂停测试的执行，直到给定的 JavaScript 表达式计算结果为 `true`。
你可以使用 `waitUntil` 方法轻松实现这一点。
在将表达式传递给此方法时，不需要包含 `return` 关键字或结束分号：

```php
// 最多等待五秒，直到表达式结果为 true...
$browser->waitUntil('App.data.servers.length > 0');

// 最多等待一秒，直到表达式结果为 true...
$browser->waitUntil('App.data.servers.length > 0', 1);
```

#### 等待 Vue 表达式

`waitUntilVue` 和 `waitUntilVueIsNot` 方法可用于等待 [Vue 组件](https://vuejs.org) 的某个属性达到指定值：

```php
// 等待组件属性包含给定值...
$browser->waitUntilVue('user.name', 'Taylor', '@user');

// 等待组件属性不包含给定值...
$browser->waitUntilVueIsNot('user.name', null, '@user');
```

#### 等待 JavaScript 事件

`waitForEvent` 方法可用于暂停测试的执行，直到某个 JavaScript 事件发生：

```php
$browser->waitForEvent('load');
```

事件监听器会附加到当前作用域，默认是 `body` 元素。
如果使用作用域选择器，事件监听器将附加到匹配的元素：

```php
$browser->with('iframe', function (Browser $iframe) {
   // 等待 iframe 的 load 事件...
    $iframe->waitForEvent('load');
});
```

你也可以将选择器作为 `waitForEvent` 方法的第二个参数，
将事件监听器附加到指定的元素：

```php
$browser->waitForEvent('load', '.selector');
```



你也可以等待 `document` 和 `window` 对象上的事件：

```php
// 等待直到文档被滚动...
$browser->waitForEvent('scroll', 'document');

// 最多等待五秒直到窗口被调整大小...
$browser->waitForEvent('resize', 'window', 5);
```

#### 使用回调等待

Dusk 中的许多 “等待” 方法依赖于底层的 `waitUsing` 方法。
你可以直接使用此方法来等待给定的闭包返回 `true`。
`waitUsing` 方法接收最大等待秒数、闭包的评估间隔、闭包本身以及可选的失败消息：

```php
$browser->waitUsing(10, 1, function () use ($something) {
    return $something->isReady();
}, "Something wasn't ready in time.");
```

### 将元素滚动到可视范围内

有时你可能无法点击某个元素，因为它在浏览器的可视区域之外。
`scrollIntoView` 方法会滚动浏览器窗口，直到给定选择器的元素进入可视范围：

```php
$browser->scrollIntoView('.selector')
    ->click('.selector');
```

## 可用的断言

Dusk 提供了多种可以对你的应用进行的断言。
所有可用断言的方法如下所列：

<style>
    .collection-method-list > p {
        columns: 10.8em 3; -moz-columns: 10.8em 3; -webkit-columns: 10.8em 3;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>

<div class="collection-method-list" markdown="1">

[assertTitle](#assert-title)
[assertTitleContains](#assert-title-contains)
[assertUrlIs](#assert-url-is)
[assertSchemeIs](#assert-scheme-is)
[assertSchemeIsNot](#assert-scheme-is-not)
[assertHostIs](#assert-host-is)
[assertHostIsNot](#assert-host-is-not)
[assertPortIs](#assert-port-is)
[assertPortIsNot](#assert-port-is-not)
[assertPathBeginsWith](#assert-path-begins-with)
[assertPathEndsWith](#assert-path-ends-with)
[assertPathContains](#assert-path-contains)
[assertPathIs](#assert-path-is)
[assertPathIsNot](#assert-path-is-not)
[assertRouteIs](#assert-route-is)
[assertQueryStringHas](#assert-query-string-has)
[assertQueryStringMissing](#assert-query-string-missing)
[assertFragmentIs](#assert-fragment-is)
[assertFragmentBeginsWith](#assert-fragment-begins-with)
[assertFragmentIsNot](#assert-fragment-is-not)
[assertHasCookie](#assert-has-cookie)
[assertHasPlainCookie](#assert-has-plain-cookie)
[assertCookieMissing](#assert-cookie-missing)
[assertPlainCookieMissing](#assert-plain-cookie-missing)
[assertCookieValue](#assert-cookie-value)
[assertPlainCookieValue](#assert-plain-cookie-value)
[assertSee](#assert-see)
[assertDontSee](#assert-dont-see)
[assertSeeIn](#assert-see-in)
[assertDontSeeIn](#assert-dont-see-in)
[assertSeeAnythingIn](#assert-see-anything-in)
[assertSeeNothingIn](#assert-see-nothing-in)
[assertScript](#assert-script)
[assertSourceHas](#assert-source-has)
[assertSourceMissing](#assert-source-missing)
[assertSeeLink](#assert-see-link)
[assertDontSeeLink](#assert-dont-see-link)
[assertInputValue](#assert-input-value)
[assertInputValueIsNot](#assert-input-value-is-not)
[assertChecked](#assert-checked)
[assertNotChecked](#assert-not-checked)
[assertIndeterminate](#assert-indeterminate)
[assertRadioSelected](#assert-radio-selected)
[assertRadioNotSelected](#assert-radio-not-selected)
[assertSelected](#assert-selected)
[assertNotSelected](#assert-not-selected)
[assertSelectHasOptions](#assert-select-has-options)
[assertSelectMissingOptions](#assert-select-missing-options)
[assertSelectHasOption](#assert-select-has-option)
[assertSelectMissingOption](#assert-select-missing-option)
[assertValue](#assert-value)
[assertValueIsNot](#assert-value-is-not)
[assertAttribute](#assert-attribute)
[assertAttributeMissing](#assert-attribute-missing)
[assertAttributeContains](#assert-attribute-contains)
[assertAttributeDoesntContain](#assert-attribute-doesnt-contain)
[assertAriaAttribute](#assert-aria-attribute)
[assertDataAttribute](#assert-data-attribute)
[assertVisible](#assert-visible)
[assertPresent](#assert-present)
[assertNotPresent](#assert-not-present)
[assertMissing](#assert-missing)
[assertInputPresent](#assert-input-present)
[assertInputMissing](#assert-input-missing)
[assertDialogOpened](#assert-dialog-opened)
[assertEnabled](#assert-enabled)
[assertDisabled](#assert-disabled)
[assertButtonEnabled](#assert-button-enabled)
[assertButtonDisabled](#assert-button-disabled)
[assertFocused](#assert-focused)
[assertNotFocused](#assert-not-focused)
[assertAuthenticated](#assert-authenticated)
[assertGuest](#assert-guest)
[assertAuthenticatedAs](#assert-authenticated-as)
[assertVue](#assert-vue)
[assertVueIsNot](#assert-vue-is-not)
[assertVueContains](#assert-vue-contains)
[assertVueDoesntContain](#assert-vue-doesnt-contain)

</div>



#### assertTitle

断言页面标题与给定文本匹配：

```php
$browser->assertTitle($title);
```

#### assertTitleContains

断言页面标题包含给定文本：

```php
$browser->assertTitleContains($title);
```

#### assertUrlIs

断言当前 URL（不含查询字符串）与给定字符串匹配：

```php
$browser->assertUrlIs($url);
```

#### assertSchemeIs

断言当前 URL 的协议与给定协议匹配：

```php
$browser->assertSchemeIs($scheme);
```

#### assertSchemeIsNot

断言当前 URL 的协议不与给定协议匹配：

```php
$browser->assertSchemeIsNot($scheme);
```

#### assertHostIs

断言当前 URL 的主机名与给定主机匹配：

```php
$browser->assertHostIs($host);
```

#### assertHostIsNot

断言当前 URL 的主机名不与给定主机匹配：

```php
$browser->assertHostIsNot($host);
```

#### assertPortIs

断言当前 URL 的端口与给定端口匹配：

```php
$browser->assertPortIs($port);
```

#### assertPortIsNot

断言当前 URL 的端口不与给定端口匹配：

```php
$browser->assertPortIsNot($port);
```

#### assertPathBeginsWith

断言当前 URL 路径以给定路径开头：

```php
$browser->assertPathBeginsWith('/home');
```

#### assertPathEndsWith

断言当前 URL 路径以给定路径结尾：

```php
$browser->assertPathEndsWith('/home');
```

#### assertPathContains

断言当前 URL 路径包含给定路径：

```php
$browser->assertPathContains('/home');
```

#### assertPathIs

断言当前路径与给定路径匹配：

```php
$browser->assertPathIs('/home');
```



#### assertPathIsNot

断言当前路径不与给定路径匹配：

```php
$browser->assertPathIsNot('/home');
```

#### assertRouteIs

断言当前 URL 与给定[命名路由](/docs/laravel/12.x/routing#named-routes)的 URL 匹配：

```php
$browser->assertRouteIs($name, $parameters);
```

#### assertQueryStringHas

断言给定的查询字符串参数存在：

```php
$browser->assertQueryStringHas($name);
```

断言给定的查询字符串参数存在并具有指定的值：

```php
$browser->assertQueryStringHas($name, $value);
```

#### assertQueryStringMissing

断言给定的查询字符串参数不存在：

```php
$browser->assertQueryStringMissing($name);
```

#### assertFragmentIs

断言 URL 当前的哈希片段与给定片段匹配：

```php
$browser->assertFragmentIs('anchor');
```

#### assertFragmentBeginsWith

断言 URL 当前的哈希片段以给定片段开头：

```php
$browser->assertFragmentBeginsWith('anchor');
```

#### assertFragmentIsNot

断言 URL 当前的哈希片段不与给定片段匹配：

```php
$browser->assertFragmentIsNot('anchor');
```

#### assertHasCookie

断言给定的加密 Cookie 存在：

```php
$browser->assertHasCookie($name);
```

#### assertHasPlainCookie

断言给定的未加密 Cookie 存在：

```php
$browser->assertHasPlainCookie($name);
```

#### assertCookieMissing

断言给定的加密 Cookie 不存在：

```php
$browser->assertCookieMissing($name);
```

#### assertPlainCookieMissing

断言给定的未加密 Cookie 不存在：

```php
$browser->assertPlainCookieMissing($name);
```

#### assertCookieValue

断言加密 Cookie 具有给定值：

```php
$browser->assertCookieValue($name, $value);
```



#### assertPlainCookieValue

断言给定的未加密 Cookie 具有指定的值：

```php
$browser->assertPlainCookieValue($name, $value);
```

#### assertSee

断言页面上存在给定的文本：

```php
$browser->assertSee($text);
```

#### assertDontSee

断言页面上不存在给定的文本：

```php
$browser->assertDontSee($text);
```

#### assertSeeIn

断言在指定的选择器内存在给定的文本：

```php
$browser->assertSeeIn($selector, $text);
```

#### assertDontSeeIn

断言在指定的选择器内不存在给定的文本：

```php
$browser->assertDontSeeIn($selector, $text);
```

#### assertSeeAnythingIn

断言在指定的选择器内存在任意文本：

```php
$browser->assertSeeAnythingIn($selector);
```

#### assertSeeNothingIn

断言在指定的选择器内不存在任何文本：

```php
$browser->assertSeeNothingIn($selector);
```

#### assertScript

断言给定的 JavaScript 表达式的结果等于指定值：

```php
$browser->assertScript('window.isLoaded')
    ->assertScript('document.readyState', 'complete');
```

#### assertSourceHas

断言页面源码中存在给定的代码：

```php
$browser->assertSourceHas($code);
```

#### assertSourceMissing

断言页面源码中不存在给定的代码：

```php
$browser->assertSourceMissing($code);
```

#### assertSeeLink

断言页面上存在给定的链接：

```php
$browser->assertSeeLink($linkText);
```

#### assertDontSeeLink

断言页面上不存在给定的链接：

```php
$browser->assertDontSeeLink($linkText);
```

#### assertInputValue

断言给定的输入字段具有指定的值：

```php
$browser->assertInputValue($field, $value);
```



#### assertInputValueIsNot

断言给定的输入字段不具有指定的值：

```php
$browser->assertInputValueIsNot($field, $value);
```

#### assertChecked

断言给定的复选框已被选中：

```php
$browser->assertChecked($field);
```

#### assertNotChecked

断言给定的复选框未被选中：

```php
$browser->assertNotChecked($field);
```

#### assertIndeterminate

断言给定的复选框处于不确定状态：

```php
$browser->assertIndeterminate($field);
```

#### assertRadioSelected

断言给定的单选框字段已选中指定的值：

```php
$browser->assertRadioSelected($field, $value);
```

#### assertRadioNotSelected

断言给定的单选框字段未选中指定的值：

```php
$browser->assertRadioNotSelected($field, $value);
```

#### assertSelected

断言给定的下拉框已选中指定的值：

```php
$browser->assertSelected($field, $value);
```

#### assertNotSelected

断言给定的下拉框未选中指定的值：

```php
$browser->assertNotSelected($field, $value);
```

#### assertSelectHasOptions

断言给定的值数组可供选择：

```php
$browser->assertSelectHasOptions($field, $values);
```

#### assertSelectMissingOptions

断言给定的值数组不可供选择：

```php
$browser->assertSelectMissingOptions($field, $values);
```

#### assertSelectHasOption

断言在给定字段中可供选择指定的值：

```php
$browser->assertSelectHasOption($field, $value);
```

#### assertSelectMissingOption

断言不可在给定字段中选择指定的值

```php
$browser->assertSelectMissingOption($field, $value);
```

#### assertValue

断言匹配给定选择器的元素具有指定的值：

```php
$browser->assertValue($selector, $value);
```



#### assertValueIsNot

断言匹配给定选择器的元素不具有指定的值：

```php
$browser->assertValueIsNot($selector, $value);
```

#### assertAttribute

断言匹配给定选择器的元素在指定属性中具有给定的值：

```php
$browser->assertAttribute($selector, $attribute, $value);
```

#### assertAttributeMissing

断言匹配给定选择器的元素缺少指定的属性：

```php
$browser->assertAttributeMissing($selector, $attribute);
```

#### assertAttributeContains

断言匹配给定选择器的元素在指定属性中包含给定的值：

```php
$browser->assertAttributeContains($selector, $attribute, $value);
```

#### assertAttributeDoesntContain

断言匹配给定选择器的元素在指定属性中不包含给定的值：

```php
$browser->assertAttributeDoesntContain($selector, $attribute, $value);
```

#### assertAriaAttribute

断言匹配给定选择器的元素在指定的 ARIA 属性中具有给定的值：

```php
$browser->assertAriaAttribute($selector, $attribute, $value);
```

例如，给定以下标记 `<button aria-label="Add"></button>`，你可以像这样断言 `aria-label` 属性：

```php
$browser->assertAriaAttribute('button', 'label', 'Add')
```

#### assertDataAttribute

断言匹配给定选择器的元素在指定的 `data` 属性中具有给定的值：

```php
$browser->assertDataAttribute($selector, $attribute, $value);
```

例如，给定以下标记 `<tr id="row-1" data-content="attendees"></tr>`，你可以像这样断言 `data-content` 属性：

```php
$browser->assertDataAttribute('#row-1', 'content', 'attendees')
```

#### assertVisible

断言匹配给定选择器的元素是可见的：

```php
$browser->assertVisible($selector);
```



#### assertPresent

断言匹配给定选择器的元素在源码中存在：

```php
$browser->assertPresent($selector);
```

#### assertNotPresent

断言匹配给定选择器的元素在源码中不存在：

```php
$browser->assertNotPresent($selector);
```

#### assertMissing

断言匹配给定选择器的元素不可见：

```php
$browser->assertMissing($selector);
```

#### assertInputPresent

断言存在具有给定名称的输入框：

```php
$browser->assertInputPresent($name);
```

#### assertInputMissing

断言具有给定名称的输入框在源码中不存在：

```php
$browser->assertInputMissing($name);
```

#### assertDialogOpened

断言已打开具有给定消息的 JavaScript 对话框：

```php
$browser->assertDialogOpened($message);
```

#### assertEnabled

断言给定字段是启用状态：

```php
$browser->assertEnabled($field);
```

#### assertDisabled

断言给定字段是禁用状态：

```php
$browser->assertDisabled($field);
```

#### assertButtonEnabled

断言给定按钮是启用状态：

```php
$browser->assertButtonEnabled($button);
```

#### assertButtonDisabled

断言给定按钮是禁用状态：

```php
$browser->assertButtonDisabled($button);
```

#### assertFocused

断言给定字段获得了焦点：

```php
$browser->assertFocused($field);
```

#### assertNotFocused

断言给定字段未获得焦点：

```php
$browser->assertNotFocused($field);
```

#### assertAuthenticated

断言用户已通过身份验证：

```php
$browser->assertAuthenticated();
```

#### assertGuest

断言用户未通过身份验证：

```php
$browser->assertGuest();
```



#### assertAuthenticatedAs

断言用户已作为给定用户通过身份验证：

```php
$browser->assertAuthenticatedAs($user);
```

#### assertVue

Dusk 甚至允许你对 [Vue 组件](https://vuejs.org) 数据的状态进行断言。
例如，假设你的应用包含以下 Vue 组件：

    // HTML...

    <profile dusk="profile-component"></profile>

    // 组件定义...

    Vue.component('profile', {
        template: '<div>{{ user.name }}</div>',

        data: function () {
            return {
                user: {
                    name: 'Taylor'
                }
            };
        }
    });

你可以像这样对 Vue 组件的状态进行断言：

```php tab=Pest
test('vue', function () {
    $this->browse(function (Browser $browser) {
        $browser->visit('/')
            ->assertVue('user.name', 'Taylor', '@profile-component');
    });
});
```

```php tab=PHPUnit
/**
 * 一个基础的 Vue 测试示例
 */
public function test_vue(): void
{
    $this->browse(function (Browser $browser) {
        $browser->visit('/')
            ->assertVue('user.name', 'Taylor', '@profile-component');
    });
}
```

#### assertVueIsNot

断言给定 Vue 组件的数据属性与给定值不匹配：

```php
$browser->assertVueIsNot($property, $value, $componentSelector = null);
```

#### assertVueContains

断言给定 Vue 组件的数据属性是数组，并且包含给定值

```php
$browser->assertVueContains($property, $value, $componentSelector = null);
```

#### assertVueDoesntContain

断言给定 Vue 组件的数据属性是数组，并且不包含给定值

```php
$browser->assertVueDoesntContain($property, $value, $componentSelector = null);
```

## 页面

有时，测试需要按顺序执行几个复杂的操作，这会让测试更难阅读和理解。
Dusk 的页面功能允许你定义可读性强的操作，然后在某个页面上通过单个方法执行它们。
页面功能还允许你为整个应用或单个页面定义常用选择器的快捷方式。



### 生成页面

要生成一个页面对象，请执行 `dusk:page` Artisan 命令。
所有页面对象将被放置在应用的 `tests/Browser/Pages` 目录中

```shell
php artisan dusk:page Login
```

### 配置页面

默认情况下，页面有三个方法：`url`、`assert` 和 `elements`。
我们现在将讨论 `url` 和 `assert` 方法。
`elements` 方法会在[下面更详细地讨论](#shorthand-selectors)。

#### `url`方法

`url` 方法应返回表示页面的 URL 路径。
Dusk 会在浏览器中导航到该页面时使用这个 URL：

```php
/**
 * 获取页面的 URL。
 */
public function url(): string
{
    return '/login';
}
```

#### `assert` 方法

`assert` 方法可以执行任何必要的断言，以验证浏览器实际上在给定的页面上。
实际上，这个方法中并不一定需要放任何东西；
然而，如果你愿意，你可以编写这些断言。
在导航到页面时，这些断言会被自动运行

```php
/**
 * 断言浏览器在该页面上。
 */
public function assert(Browser $browser): void
{
    $browser->assertPathIs($this->url());
}
```

### 导航到页面

一旦页面被定义，你可以使用 `visit` 方法导航到它：

```php
use Tests\Browser\Pages\Login;

$browser->visit(new Login);
```

有时，你可能已经在某个页面上，并且需要将页面的选择器和方法“加载”到当前测试上下文中。
当点击一个按钮并被重定向到某个页面，而不是显式地导航到它时，这种情况很常见。
在这种情况下，你可以使用 `on` 方法来加载页面：

```php
use Tests\Browser\Pages\CreatePlaylist;

$browser->visit('/dashboard')
    ->clickLink('Create Playlist')
    ->on(new CreatePlaylist)
    ->assertSee('@create');
```



### 简写选择器

页面类中的 `elements` 方法允许你为页面上的任意 CSS 选择器定义快速、易于记忆的快捷方式。
例如，我们来为应用程序登录页面的 “email” 输入字段定义一个快捷方式：

```php
/**
 * 获取页面的元素快捷方式。
 *
 * @return array<string, string>
 */
public function elements(): array
{
    return [
        '@email' => 'input[name=email]',
    ];
}
```

一旦定义了快捷方式，你就可以在任何通常使用完整 CSS 选择器的地方使用这个简写选择器：

```php
$browser->type('@email', 'taylor@laravel.com');
```

#### 全局简写选择器

安装 Dusk 之后，一个基础 `Page` 类会被放置在你的 `tests/Browser/Pages` 目录中。
这个类包含一个 `siteElements` 方法，可用于定义全局简写选择器，这些选择器在整个应用程序的每个页面中都可用：

```php
/**
 * 获取站点的全局元素快捷方式。
 *
 * @return array<string, string>
 */
public static function siteElements(): array
{
    return [
        '@element' => '#selector',
    ];
}
```

### 页面方法

除了页面上定义的默认方法外，你还可以定义额外的方法，这些方法可以在整个测试中使用。
例如，假设我们正在构建一个音乐管理应用程序。
该应用程序的某个页面上的常见操作可能是创建播放列表。
与其在每个测试中都重复编写创建播放列表的逻辑，不如在页面类上定义一个 `createPlaylist` 方法：
```php
<?php

namespace Tests\Browser\Pages;

use Laravel\Dusk\Browser;
use Laravel\Dusk\Page;

class Dashboard extends Page
{
    // 其他页面方法...
    /**
     * 创建一个新的播放列表。
     */
    public function createPlaylist(Browser $browser, string $name): void
    {
        $browser->type('name', $name)
            ->check('share')
            ->press('Create Playlist');
    }
}
```



一旦方法被定义，你就可以在任何使用该页面的测试中调用它。
浏览器实例会自动作为自定义页面方法的第一个参数传入：

```php
use Tests\Browser\Pages\Dashboard;

$browser->visit(new Dashboard)
    ->createPlaylist('My Playlist')
    ->assertSee('My Playlist');
```

## 组件

组件类似于 Dusk 的 “页面对象（page objects）”，
但它们是为在整个应用中重复使用的 UI 和功能而设计的，比如导航栏或通知窗口。
因此，组件并不绑定到特定的 URL。

### 生成组件

要生成一个组件，请执行 `dusk:component` Artisan 命令。
新的组件会放置在 `tests/Browser/Components` 目录中：

```shell
php artisan dusk:component DatePicker
```

如上所示，“日期选择器” 是一个组件的例子，
它可能在应用程序的多个页面中都会出现。
如果你在测试套件中的几十个测试中都要手动编写选择日期的浏览器自动化逻辑，那会很繁琐。
相反，我们可以定义一个 Dusk 组件来表示日期选择器，把这些逻辑封装到组件中：

```php
<?php

namespace Tests\Browser\Components;

use Laravel\Dusk\Browser;
use Laravel\Dusk\Component as BaseComponent;

class DatePicker extends BaseComponent
{
    /**
     * 获取组件的根选择器。
     */
    public function selector(): string
    {
        return '.date-picker';
    }

    /**
     * 断言浏览器页面包含该组件。
     */
    public function assert(Browser $browser): void
    {
        $browser->assertVisible($this->selector());
    }

    /**
     * 获取组件的元素快捷方式。
     *
     * @return array<string, string>
     */
    public function elements(): array
    {
        return [
            '@date-field' => 'input.datepicker-input',
            '@year-list' => 'div > div.datepicker-years',
            '@month-list' => 'div > div.datepicker-months',
            '@day-list' => 'div > div.datepicker-days',
        ];
    }

    /**
     * 选择指定的日期。
     */
    public function selectDate(Browser $browser, int $year, int $month, int $day): void
    {
        $browser->click('@date-field')
            ->within('@year-list', function (Browser $browser) use ($year) {
                $browser->click($year);
            })
            ->within('@month-list', function (Browser $browser) use ($month) {
                $browser->click($month);
            })
            ->within('@day-list', function (Browser $browser) use ($day) {
                $browser->click($day);
            });
    }
}
```



### 使用组件

一旦定义了组件，我们就可以在任何测试中轻松地在日期选择器中选择日期。
并且，如果选择日期所需的逻辑发生变化，我们只需要更新组件即可：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\Browser\Components\DatePicker;

uses(DatabaseMigrations::class);

test('basic example', function () {
    $this->browse(function (Browser $browser) {
        $browser->visit('/')
            ->within(new DatePicker, function (Browser $browser) {
                $browser->selectDate(2019, 1, 30);
            })
            ->assertSee('January');
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Browser;

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\Browser\Components\DatePicker;
use Tests\DuskTestCase;

class ExampleTest extends DuskTestCase
{
    /**
     * 一个基础组件测试示例。
     */
    public function test_basic_example(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/')
                ->within(new DatePicker, function (Browser $browser) {
                    $browser->selectDate(2019, 1, 30);
                })
                ->assertSee('January');
        });
    }
}
```

## 持续集成

> [!警告]
> 大多数 Dusk 持续集成配置都期望你的 Laravel 应用在端口 8000 上使用内置的 PHP 开发服务器运行。因此，在继续之前，你应确保你的持续集成环境中 `APP_URL` 环境变量的值为 `http://127.0.0.1:8000`。

### Heroku CI

要在 [Heroku CI](https://www.heroku.com/continuous-integration) 上运行 Dusk 测试，请在 Heroku 的 `app.json` 文件中添加以下 Google Chrome buildpack 和脚本：

```json
{
  "environments": {
    "test": {
      "buildpacks": [
        { "url": "heroku/php" },
        { "url": "https://github.com/heroku/heroku-buildpack-chrome-for-testing" }
      ],
      "scripts": {
        "test-setup": "cp .env.testing .env",
        "test": "nohup bash -c './vendor/laravel/dusk/bin/chromedriver-linux --port=9515 > /dev/null 2>&1 &' && nohup bash -c 'php artisan serve --no-reload > /dev/null 2>&1 &' && php artisan dusk"
      }
    }
  }
}
```



### Travis CI

要在 [Travis CI](https://travis-ci.org) 上运行你的 Dusk 测试，请使用以下 `.travis.yml` 配置。
由于 Travis CI 不是图形化环境，我们需要采取一些额外步骤来启动 Chrome 浏览器。
此外，我们将使用 `php artisan serve` 启动 PHP 的内置 Web 服务器：

```yaml
language: php

php:
  - 8.2

addons:
  chrome: stable

install:
  - cp .env.testing .env
  - travis_retry composer install --no-interaction --prefer-dist
  - php artisan key:generate
  - php artisan dusk:chrome-driver

before_script:
  - google-chrome-stable --headless --disable-gpu --remote-debugging-port=9222 http://localhost &
  - php artisan serve --no-reload &

script:
  - php artisan dusk
```

### GitHub Actions

如果你使用 [GitHub Actions](https://github.com/features/actions) 运行 Dusk 测试，可以使用以下配置文件作为起点。
与 Travis CI 一样，我们将使用 `php artisan serve` 命令来启动 PHP 的内置 Web 服务器：

```yaml
name: CI
on: [push]
jobs:

  dusk-php:
    runs-on: ubuntu-latest
    env:
      APP_URL: "http://127.0.0.1:8000"
      DB_USERNAME: root
      DB_PASSWORD: root
      MAIL_MAILER: log
    steps:
      - uses: actions/checkout@v4
      - name: Prepare The Environment
        run: cp .env.example .env
      - name: Create Database
        run: |
          sudo systemctl start mysql
          mysql --user="root" --password="root" -e "CREATE DATABASE \`my-database\` character set UTF8mb4 collate utf8mb4_bin;"
      - name: Install Composer Dependencies
        run: composer install --no-progress --prefer-dist --optimize-autoloader
      - name: Generate Application Key
        run: php artisan key:generate
      - name: Upgrade Chrome Driver
        run: php artisan dusk:chrome-driver --detect
      - name: Start Chrome Driver
        run: ./vendor/laravel/dusk/bin/chromedriver-linux --port=9515 &
      - name: Run Laravel Server
        run: php artisan serve --no-reload &
      - name: Run Dusk Tests
        run: php artisan dusk
      - name: Upload Screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots
          path: tests/Browser/screenshots
      - name: Upload Console Logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: console
          path: tests/Browser/console
```



### Chipper CI

如果你使用 [Chipper CI](https://chipperci.com) 来运行 Dusk 测试，你可以使用以下配置文件作为起点。
我们将使用 PHP 的内置服务器运行 Laravel，以便可以监听请求：

```yaml
# file .chipperci.yml
version: 1

environment:
  php: 8.2
  node: 16

# Include Chrome in the build environment
services:
  - dusk

# Build all commits
on:
   push:
      branches: .*

pipeline:
  - name: Setup
    cmd: |
      cp -v .env.example .env
      composer install --no-interaction --prefer-dist --optimize-autoloader
      php artisan key:generate

      # 创建一个 dusk 环境文件，确保 APP_URL 使用 BUILD_HOST
      cp -v .env .env.dusk.ci
      sed -i "s@APP_URL=.*@APP_URL=http://$BUILD_HOST:8000@g" .env.dusk.ci

  - name: Compile Assets
    cmd: |
      npm ci --no-audit
      npm run build

  - name: Browser Tests
    cmd: |
      php -S [::0]:8000 -t public 2>server.log &
      sleep 2
      php artisan dusk:chrome-driver $CHROME_DRIVER
      php artisan dusk --env=ci
```

要了解更多在 Chipper CI 上运行 Dusk 测试的内容，包括如何使用数据库，请查阅 [Chipper CI 官方文档](https://chipperci.com/docs/testing/laravel-dusk-new/)。
