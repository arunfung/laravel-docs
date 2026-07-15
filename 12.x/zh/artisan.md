# Artisan Console

- [介绍](#introduction)
  - [Tinker 命令 （REPL）](#tinker)
- [编写命令](#writing-commands)
  - [生成命令](#generating-commands)
  - [命令结构](#command-structure)
  - [闭包命令](#closure-commands)
  - [可隔离命令](#isolatable-commands)
- [定义输入期望值](#defining-input-expectations)
  - [参数](#arguments)
  - [选项](#options)
  - [输入数组](#input-arrays)
  - [输入说明](#input-descriptions)
  - [提示缺少的输入](#prompting-for-missing-input)
- [I/O 命令](#command-io)
  - [检索输入](#retrieving-input)
  - [输入提示](#prompting-for-input)
  - [编写输出](#writing-output)
- [注册命令](#registering-commands)
- [编程式执行命令](#programmatically-executing-commands)
  - [从其他命令调用命令](#calling-commands-from-other-commands)
- [信号处理](#signal-handling)
- [Stub 自定义](#stub-customization)
- [事件](#events)

<a name="introduction"></a>
## 介绍

Artisan 是 Laravel 自带的命令行接口。Artisan 以 `artisan` 脚本的方式存在于应用的根目录中，并提供了许多有用的命令，来帮你构建应用程序。你可以使用 `list` 命令查看所有可用的 Artisan 命令：

```shell
php artisan list
```

每个命令都有一个「help」帮助界面，它展示并描述了该命令的可用参数和选项。要查看帮助界面，请在命令前加上 `help` 即可：

```shell
php artisan help migrate
```

<a name="laravel-sail"></a>
#### Laravel Sail

如果你使用 [Laravel Sail](/docs/laravel/12.x/sail) 作为本地开发环境，记得使用 `sail` 命令行来调用 Artisan 命令。Sail 会在应用的 Docker 容器中执行 Artisan 命令：

```shell
./vendor/bin/sail artisan list
```

<a name="tinker"></a>
### Tinker （REPL）
[Laravel Tinker](https://github.com/laravel/tinker) 是为 Laravel 提供的一个强大的 REPL（交互式解释器），由 [PsySH](https://github.com/bobthecow/psysh) 驱动支持。



#### 安装

所有 Laravel 应用程序默认都包含 Tinker。
不过，如果你之前从应用中移除了它，可以通过 Composer 重新安装：

```shell
composer require laravel/tinker
```

> [!注意]
> 想要在与 Laravel 应用交互时支持 **热重载、多行代码编辑和自动补全** 吗？可以看看 [Tinkerwell](https://tinkerwell.app)！

#### 使用方法

Tinker 允许你在命令行与整个 Laravel 应用程序进行交互，包括 Eloquent 模型、任务 (jobs)、事件 (events) 等。
要进入 Tinker 环境，请运行 `tinker` Artisan 命令：

```shell
php artisan tinker
```

你可以通过 `vendor:publish` 命令发布 Tinker 的配置文件：

```shell
php artisan vendor:publish --provider="Laravel\Tinker\TinkerServiceProvider"
```

> [!警告]
> `dispatch` 辅助函数以及 `Dispatchable` 类中的 `dispatch` 方法依赖于垃圾回收来将任务放入队列。
因此，在使用 Tinker 时，应使用 `Bus::dispatch` 或 `Queue::push` 来派发任务。

#### 命令允许清单

Tinker 使用一个 “allow” 清单来决定在其 shell 中允许运行哪些 Artisan 命令。
默认情况下，你可以运行以下命令：
-   `clear-compiled`
-   `down`
-   `env`
-   `inspire`
-   `migrate`
-   `migrate:install`
-   `up`
-   `optimize`

```php
'commands' => [
    // App\Console\Commands\ExampleCommand::class,
],
```

#### 不应被别名化的类

通常，Tinker 会在你交互过程中自动为类添加别名。
不过，你可能希望某些类**永远不要被别名化**。
你可以在 `tinker.php` 配置文件的 `dont_alias` 数组中列出这些类：

```php
'dont_alias' => [
    App\Models\User::class,
],
```



## 编写命令

除了 Artisan 提供的命令之外，你还可以构建自己的自定义命令。命令通常存储在 `app/Console/Commands` 目录中；然而，只要你指示 Laravel [扫描其他目录中的 Artisan 命令](#registering-commands)，你也可以自由选择自己的存储位置。

### 生成命令 (Generating Commands)

要创建一个新命令，可以使用 `make:command` Artisan 命令。该命令会在 `app/Console/Commands` 目录中创建一个新的命令类。
如果应用中不存在该目录，不必担心 —— 当你第一次运行 `make:command` Artisan 命令时，它会被自动创建：

```shell
php artisan make:command SendEmails
```

### 命令结构 (Command Structure)

在生成命令之后，你应该为类的 `signature` 和 `description` 属性定义合适的值。
这些属性会在 `list` 屏幕上显示你的命令时使用。
其中，`signature` 属性还允许你定义 [命令的输入期望](#defining-input-expectations)。

当命令被执行时，`handle` 方法会被调用。你可以将命令逻辑放在这个方法中。

让我们看一个示例命令。注意，在命令的 `handle` 方法中，我们可以请求所需的任何依赖项。Laravel 的 [服务容器](/docs/laravel/12.x/container) 会自动注入所有在方法签名中通过类型提示声明的依赖：

```php
<?php

namespace App\Console\Commands;

use App\Models\User;
use App\Support\DripEmailer;
use Illuminate\Console\Command;

class SendEmails extends Command
{
    /**
     * 控制台命令的名称和签名。
     *
     * @var string
     */
    protected $signature = 'mail:send {user}';

    /**
     * 控制台命令的描述。
     *
     * @var string
     */
    protected $description = 'Send a marketing email to a user';

    /**
     * 执行控制台命令。
     */
    public function handle(DripEmailer $drip): void
    {
        $drip->send(User::find($this->argument('user')));
    }
}
```

> [!注意]
> 为了更好地复用代码，建议保持控制台命令简洁，并让它们委托给应用服务来完成任务。
在上面的示例中，请注意我们注入了一个服务类来完成发送邮件的“繁重工作”。



#### 退出码

如果 `handle` 方法没有返回任何内容并且命令成功执行，那么命令将以 `0` 退出码退出，表示成功。
但是，`handle` 方法也可以选择返回一个整数，以手动指定命令的退出码：

```php
$this->error('Something went wrong.');

return 1;
```

如果你希望从命令中的任何方法中“失败”命令，可以使用 `fail` 方法。
`fail` 方法会立即终止命令的执行并返回退出码 `1`：

```php
$this->fail('Something went wrong.');
```

### 闭包命令（Closure Commands）

基于闭包的命令提供了一种替代方案，使你不必将控制台命令定义为类。
就像路由闭包是控制器的一种替代方式一样，可以把命令闭包看作是命令类的一种替代方式。

虽然 `routes/console.php` 文件并不会定义 HTTP 路由，但它定义了进入应用的基于控制台的入口点（路由）。
在这个文件中，你可以使用 `Artisan::command` 方法来定义所有基于闭包的控制台命令。
`command` 方法接受两个参数：**命令签名** 和一个闭包，该闭包会接收命令的参数和选项：

```php
Artisan::command('mail:send {user}', function (string $user) {
    $this->info("Sending email to: {$user}!");
});
```
该闭包会绑定到底层的命令实例，因此你可以完全访问命令类中通常能用到的所有辅助方法。

#### 类型提示依赖（Type-Hinting Dependencies）

除了接收命令的参数和选项外，命令闭包还可以类型提示你希望从 [服务容器](/docs/laravel/12.x/container) 中解析的其他依赖：


```php
use App\Models\User;
use App\Support\DripEmailer;

Artisan::command('mail:send {user}', function (DripEmailer $drip, string $user) {
    $drip->send(User::find($user));
});
```



#### 闭包命令描述（Closure Command Descriptions）

在定义基于闭包的命令时，你可以使用 `purpose` 方法为命令添加描述。
当你运行 `php artisan list` 或 `php artisan help` 时，这个描述会被显示出来：

```php
Artisan::command('mail:send {user}', function (string $user) {
    // ...
})->purpose('Send a marketing email to a user');
```
### 可隔离命令

> [!警告]
> 若要使用此功能，你的应用必须使用以下其中一种作为默认缓存驱动：
> `memcached`、`redis`、`dynamodb`、`database`、`file` 或 `array`。
> 此外，所有服务器必须连接到同一个中央缓存服务器。

有时候，你可能希望确保某个命令**同一时间只能运行一个实例**。
要实现这一点，你可以在命令类上实现 `Illuminate\Contracts\Console\Isolatable` 接口：

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Contracts\Console\Isolatable;

class SendEmails extends Command implements Isolatable
{
    // ...
}
```

当命令被标记为 `Isolatable` 后，Laravel 会自动为该命令添加一个 `--isolated` 选项。
当你在运行命令时加上该选项，Laravel 会确保没有其他相同命令实例正在运行。
Laravel 通过应用的默认缓存驱动尝试获取一个**原子锁**来实现这一点。

如果发现已有其他实例在运行，该命令将不会执行；但命令仍然会以**成功的退出状态码**退出：

```shell
php artisan mail:send 1 --isolated
```

如果你希望在命令无法执行时指定退出状态码，可以通过 `isolated` 选项传入你想要的状态码：

```shell
php artisan mail:send 1 --isolated=12
```



#### 锁 ID（Lock ID）

默认情况下，Laravel 会使用**命令的名称**来生成字符串键（key），该键用于在应用的缓存中获取原子锁。不过，你也可以通过在 Artisan 命令类中定义 `isolatableId` 方法来自定义这个 key。
这样你就可以把命令的参数或选项整合进 key 中：

```php
/**
 * 获取命令的隔离 ID。
 */
public function isolatableId(): string
{
    return $this->argument('user');
}
```
#### 锁过期时间

默认情况下，隔离锁会在命令执行完成后自动过期。
或者，如果命令被中断而未能完成，锁会在 **1 小时后**过期。

你也可以通过在命令中定义 `isolationLockExpiresAt` 方法，来自定义锁的过期时间：

```php
use DateTimeInterface;
use DateInterval;

/**
 * 决定命令的隔离锁何时过期。
 */
public function isolationLockExpiresAt(): DateTimeInterface|DateInterval
{
    return now()->addMinutes(5);
}
```

## 定义输入预期（Defining Input Expectations）

在编写控制台命令时，我们通常需要通过**参数（arguments）**或**选项（options）**来收集用户输入。
Laravel 提供了一种非常方便的方式 —— 使用命令类中的 `signature` 属性来定义你期望的输入。
`signature` 属性允许你用一种类似路由的直观语法，在一行中定义命令的名称、参数和选项。

### 参数（Arguments）

所有用户传入的 **参数** 和 **选项** 都用大括号 `{}` 包裹。
例如，下面的命令定义了一个必填参数：`user`：

```php
/**
 * 命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send {user}';
```



你也可以让参数变成**可选**，或者为参数定义一个**默认值**：

```php
// 可选参数...
'mail:send {user?}'

// 带默认值的可选参数...
'mail:send {user=foo}'
```

### 选项（Options）

选项（Options）和参数类似，也是另一种用户输入方式。
选项在命令行中以两个短横线（`--`）开头。
选项分为两类：

1.  **带值的选项**（需要用户传入具体的值）
2.  **不带值的选项**（布尔开关，用来控制某个功能开/关）
    我们先来看一个**布尔开关**类型的例子：


```php
/**
 * 命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send {user} {--queue}';
```

在这个例子中，调用 Artisan 命令时，可以指定 `--queue` 选项。
如果传入了 `--queue`，那么该选项的值为 `true`；
如果没有传入，则该选项的值为 `false`：

```shell
php artisan mail:send 1 --queue
```

#### 带值的选项（Options With Values）

接下来，我们看看需要传入**值**的选项。
如果用户必须为某个选项指定值，那么需要在选项名后面加上 `=`：

```php
/**
 * 命令的名称和签名。
 *
 * @var string
 */
protected $signature = 'mail:send {user} {--queue=}';
```

在这个例子中，用户可以这样传值：
如果调用命令时没有传入 `--queue`，那么其值将是 `null`：

```shell
php artisan mail:send 1 --queue=default
```

你也可以为选项定义一个默认值：
如果用户没有传入该选项，那么会使用默认值：

```php
'mail:send {user} {--queue=default}'
```



#### 选项快捷方式（Option Shortcuts）

在定义选项时，你可以为它指定一个**快捷方式**。
使用 `|` 作为分隔符，将快捷方式和完整选项名写在一起即可：

```php
'mail:send {user} {--Q|queue}'
```

在终端调用命令时，选项的快捷方式前缀使用**单个短横线**（`-`）。
如果选项需要值，注意**不能带 `=`**，而是紧跟在快捷方式后面：

```shell
php artisan mail:send 1 -Qdefault
```

### 输入数组（Input Arrays）

如果你希望某个参数或选项接收**多个输入值**，可以在定义时加上 `*`。
先来看一个参数数组的例子：

```php
'mail:send {user*}'
```

执行命令时，`user` 参数可以连续传入多个值。
比如下面的命令会让 `user` 参数的值变成一个数组 `[1, 2]`：

```shell
php artisan mail:send 1 2
```

`*` 也可以和 **可选参数** 一起使用，允许传入零个或多个值：

```php
'mail:send {user?*}'
```

#### 选项数组（Option Arrays）

如果你希望某个**选项**能接收多个值，可以这样定义：

```php
'mail:send {--id=*}'
```

调用时，用户可以多次传入同名选项，每个值会自动收集成一个数组：

```shell
php artisan mail:send --id=1 --id=2
```

### 输入描述（Input Descriptions）

你可以为参数和选项添加**描述信息**，只需在定义时用冒号分隔名称和说明。
如果定义太长，可以换行书写，保持清晰：

```php
/**
 * The name and signature of the console command.
 *
 * @var string
 */
protected $signature = 'mail:send
                        {user : The ID of the user}
                        {--queue : Whether the job should be queued}';
```



### 提示缺失的输入

如果你的命令包含必填参数，但用户在执行时没有提供这些参数，那么用户会收到一条错误信息。
作为替代方案，你也可以让命令在缺少必填参数时**自动提示用户输入**，只需要实现 `PromptsForMissingInput` 接口即可：

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Contracts\Console\PromptsForMissingInput;

class SendEmails extends Command implements PromptsForMissingInput
{
    /**
     * 命令的名称和签名。
     *
     * @var string
     */
    protected $signature = 'mail:send {user}';

    // ...
}
```

如果 Laravel 需要从用户那里收集必填参数，它会自动向用户提问，
并会**智能地使用参数名或参数描述来组织问题**。

如果你希望自定义提示用户输入的提问方式，可以实现 `promptForMissingArgumentsUsing` 方法，
并返回一个**以参数名为键、问题为值**的数组：

```php
/**
 * 使用返回的问题来提示缺失的输入参数。
 *
 * @return array<string, string>
 */
protected function promptForMissingArgumentsUsing(): array
{
    return [
        'user' => 'Which user ID should receive the mail?',
    ];
}
```

你还可以通过**元组**的方式，提供提示问题和占位符（placeholder）：

```php
return [
    'user' => ['Which user ID should receive the mail?', 'E.g. 123'],
];
```

如果你想对提示过程拥有完全的控制权，你可以提供一个 **闭包**，
由该闭包负责提示用户并返回答案：

```php
use App\Models\User;
use function Laravel\Prompts\search;

// ...

return [
    'user' => fn () => search(
        label: 'Search for a user:',
        placeholder: 'E.g. Taylor Otwell',
        options: fn ($value) => strlen($value) > 0
            ? User::where('name', 'like', "%{$value}%")->pluck('name', 'id')->all()
            : []
    ),
];
```

> [!注意]
更完整的 [Laravel Prompts](/docs/laravel/12.x/prompts) 文档包含了关于可用提示及其用法的更多信息。



如果你希望提示用户去选择或输入[选项](#options)，你可以在命令的 `handle` 方法中包含提示。
然而，如果你只希望在用户**已经因为缺失参数而被自动提示之后**再进一步提示用户，那么你可以实现 `afterPromptingForMissingArguments` 方法：

```php
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use function Laravel\Prompts\confirm;

// ...

/**
 * 在用户被提示输入缺失参数之后执行操作。
 */
protected function afterPromptingForMissingArguments(InputInterface $input, OutputInterface $output): void
{
    $input->setOption('queue', confirm(
        label: 'Would you like to queue the mail?',
        default: $this->option('queue')
    ));
}
```

## 命令的输入 / 输出（Command I/O）

### 获取输入（Retrieving Input）

当你的命令在执行时，你很可能需要访问命令所接受的参数和选项的值。
要做到这一点，你可以使用 `argument` 和 `option` 方法。
如果某个参数或选项不存在，将会返回 `null`：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $userId = $this->argument('user');
}
```

如果你需要将所有参数一次性作为 `array` 获取，可以调用 `arguments` 方法：

```php
$arguments = $this->arguments();
```

选项（Options）的获取方式和参数一样简单：你可以使用 `option` 方法。
如果你想要将所有选项一次性作为数组获取，可以调用 `options` 方法：

```php
// 获取某个具体的选项...
$queueName = $this->option('queue');

// 获取所有选项作为数组...
$options = $this->options();
```

### 提示输入（Prompting for Input）

> [!注意]
> [Laravel Prompts](/docs/laravel/12.x/prompts) 是一个 PHP 包，用于为命令行应用添加美观且用户友好的表单，
> 它提供了类似浏览器的功能，包括**占位符文本**和**输入验证**。



除了显示输出之外，你还可以在命令执行过程中要求用户提供输入。
`ask` 方法会向用户显示给定的问题，接收他们的输入，然后将用户输入返回给你的命令：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $name = $this->ask('What is your name?');

    // ...
}
```

`ask` 方法还可以接受一个可选的第二个参数，用来指定如果用户没有输入时应返回的默认值：

```php
$name = $this->ask('What is your name?', 'Taylor');
```

`secret` 方法和 `ask` 类似，但用户在控制台输入时不会显示他们的输入。
此方法在请求敏感信息（例如密码）时非常有用：

```php
$password = $this->secret('What is the password?');
```

#### 请求确认（Asking for Confirmation）

如果你需要向用户请求一个简单的“是或否”确认，可以使用 `confirm` 方法。
默认情况下，该方法会返回 `false`。但是，如果用户在提示中输入 `y` 或 `yes`，方法将返回 `true`：

```php
if ($this->confirm('Do you wish to continue?')) {
    // ...
}
```

如有必要，你可以通过向 `confirm` 方法传递第二个参数 `true` 来指定确认提示的默认值为 `true`：

```php
if ($this->confirm('Do you wish to continue?', true)) {
    // ...
}
```

#### 自动完成（Auto-Completion）

`anticipate` 方法可用于提供可能选择的自动完成提示。
用户仍然可以输入任何答案，而不受自动完成提示的限制：

```php
$name = $this->anticipate('What is your name?', ['Taylor', 'Dayle']);
```



或者，你可以将一个闭包作为 `anticipate` 方法的第二个参数传入。
每当用户输入一个字符时，闭包就会被调用。
闭包应接受一个字符串参数，表示用户当前已输入的内容，并返回用于自动完成的选项数组：

```php
use App\Models\Address;

$name = $this->anticipate('What is your address?', function (string $input) {
    return Address::whereLike('name', "{$input}%")
        ->limit(5)
        ->pluck('name')
        ->all();
});
```

#### 多选题（Multiple Choice Questions）

如果你需要在提问时给用户一个预定义的选项集合，可以使用 `choice` 方法。
如果用户没有选择任何选项，你可以通过传入默认值的数组索引作为第三个参数来指定默认返回值：

```php
$name = $this->choice(
    'What is your name?',
    ['Taylor', 'Dayle'],
    $defaultIndex
);
```

此外，`choice` 方法还接受可选的第四和第五个参数，用于确定选择有效答案的最大尝试次数，以及是否允许多选：

```php
$name = $this->choice(
    'What is your name?',
    ['Taylor', 'Dayle'],
    $defaultIndex,
    $maxAttempts = null,
    $allowMultipleSelections = false
);
```

### 输出信息（Writing Output）

要向控制台输出信息，你可以使用 `line`、`info`、`comment`、`question`、`warn` 和 `error` 方法。
这些方法会根据用途使用合适的 ANSI 颜色。
例如，我们向用户显示一些一般信息。通常，`info` 方法在控制台中会显示为绿色文本：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    // ...

    $this->info('The command was successful!');
}
```



要显示错误信息，可以使用 `error` 方法。错误信息通常以红色显示：

```php
$this->error('Something went wrong!');
```

你可以使用 `line` 方法显示普通的、不带颜色的文本：

```php
$this->line('Display this on the screen');
```

你可以使用 `newLine` 方法显示一个空行：

```php
// 写一个空行...
$this->newLine();

// 写三个空行...
$this->newLine(3);
```

#### 表格（Tables）

`table` 方法可以方便地格式化多行多列的数据。
你只需要提供列名和表格数据，Laravel 会自动计算表格的宽度和高度：

```php
use App\Models\User;

$this->table(
    ['Name', 'Email'],
    User::all(['name', 'email'])->toArray()
);
```

#### 进度条（Progress Bars）

对于长时间运行的任务，显示进度条可以帮助用户了解任务完成的进度。
使用 `withProgressBar` 方法，Laravel 会显示一个进度条，并在遍历给定可迭代值的每个元素时推进进度：

```php
use App\Models\User;

$users = $this->withProgressBar(User::all(), function (User $user) {
    $this->performTask($user);
});
```

有时候，你可能需要更手动地控制进度条的推进。
首先，定义任务需要迭代的总步数，然后在处理每个元素后推进进度条：

```php
$users = App\Models\User::all();

$bar = $this->output->createProgressBar(count($users));

$bar->start();

foreach ($users as $user) {
    $this->performTask($user);

    $bar->advance();
}

$bar->finish();
```


> [!注意]
> 如需更多高级选项，请参考 [Symfony Progress Bar 组件文档](https://symfony.com/doc/current/components/console/helpers/progressbar.html)。



## 注册命令（Registering Commands）

默认情况下，Laravel 会自动注册 `app/Console/Commands` 目录下的所有命令。
但是，你也可以使用 `withCommands` 方法在应用的 `bootstrap/app.php` 文件中指示 Laravel 扫描其他目录的 Artisan 命令：

```php
->withCommands([
    __DIR__.'/../app/Domain/Orders/Commands',
])
```

如果需要，你还可以通过将命令类名传递给 `withCommands` 方法来手动注册命令：

```php
use App\Domain\Orders\Commands\SendEmails;

->withCommands([
    SendEmails::class,
])
```

当 Artisan 启动时，你应用中的所有命令都会由 [服务容器](/docs/laravel/12.x/container) 解析并注册到 Artisan。

## 以编程方式执行命令（Programmatically Executing Commands）

有时候，你可能希望在 CLI 之外执行 Artisan 命令。例如，你可能希望从路由或控制器中执行 Artisan 命令。
可以使用 `Artisan` 门面（Facade）的 `call` 方法来实现。
`call` 方法的第一个参数可以是命令的签名名称或类名，第二个参数是命令参数数组。方法会返回命令的退出码：

```php
use Illuminate\Support\Facades\Artisan;

Route::post('/user/{user}/mail', function (string $user) {
    $exitCode = Artisan::call('mail:send', [
        'user' => $user, '--queue' => 'default'
    ]);

    // ...
});
```

你也可以直接将完整的 Artisan 命令作为字符串传给 `call` 方法：

```php
Artisan::call('mail:send 1 --queue=default');
```

#### 传递数组值（Passing Array Values）

如果你的命令定义了一个接受数组的选项，你可以传递一个值数组给该选项：

```php
use Illuminate\Support\Facades\Artisan;

Route::post('/mail', function () {
    $exitCode = Artisan::call('mail:send', [
        '--id' => [5, 13]
    ]);
});
```



#### 传递布尔值

如果你需要为不接受字符串值的选项指定值，例如 `migrate:refresh` 命令中的 `--force` 标志，你应该将选项的值设置为 `true` 或 `false`：

```php
$exitCode = Artisan::call('migrate:refresh', [
    '--force' => true,
]);
```

#### 将 Artisan 命令入队（Queueing Artisan Commands）

使用 `Artisan` 门面的 `queue` 方法，你甚至可以将 Artisan 命令入队，由你的 [队列工作器](/docs/laravel/12.x/queues) 在后台处理。在使用此方法之前，请确保你已经配置好队列并正在运行队列监听器：

```php
use Illuminate\Support\Facades\Artisan;

Route::post('/user/{user}/mail', function (string $user) {
    Artisan::queue('mail:send', [
        'user' => $user, '--queue' => 'default'
    ]);

    // ...
});
```

使用 `onConnection` 和 `onQueue` 方法，你可以指定 Artisan 命令应派发到哪个连接或队列：

```php
Artisan::queue('mail:send', [
    'user' => 1, '--queue' => 'default'
])->onConnection('redis')->onQueue('commands');
```

### 从其他命令调用命令（Calling Commands From Other Commands）

有时，你可能希望从已有的 Artisan 命令中调用其他命令。可以使用 `call` 方法来实现。该 `call` 方法接受命令名称和一个命令参数/选项数组：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $this->call('mail:send', [
        'user' => 1, '--queue' => 'default'
    ]);

    // ...
}
```

如果你希望调用另一个控制台命令并屏蔽其所有输出，可以使用 `callSilently` 方法。`callSilently` 方法的签名与 `call` 方法相同：

```php
$this->callSilently('mail:send', [
    'user' => 1, '--queue' => 'default'
]);
```



## 信号处理（Signal Handling）

正如你所知，操作系统允许向正在运行的进程发送信号。例如，`SIGTERM` 信号是操作系统请求程序终止的方式。如果你希望在 Artisan 控制台命令中监听信号并在信号触发时执行代码，可以使用 `trap` 方法：

```php
/**
 * 执行控制台命令。
 */
public function handle(): void
{
    $this->trap(SIGTERM, fn () => $this->shouldKeepRunning = false);

    while ($this->shouldKeepRunning) {
        // ...
    }
}
```

如果希望同时监听多个信号，可以向 `trap` 方法传递一个信号数组：

```php
$this->trap([SIGTERM, SIGQUIT], function (int $signal) {
    $this->shouldKeepRunning = false;

    dump($signal); // SIGTERM / SIGQUIT
});
```

## 模板（Stub）自定义（Stub Customization）

Artisan 控制台的 `make` 命令用于创建各种类，例如控制器、作业、迁移和测试。这些类是通过“stub”文件生成的，生成内容会根据你的输入进行填充。然而，你可能希望对 Artisan 生成的文件做一些小修改。为此，你可以使用 `stub:publish` 命令将最常用的 stub 发布到你的应用中，以便进行自定义：

```shell
php artisan stub:publish
```

发布的 stub 文件会位于应用根目录下的 `stubs` 目录中。对这些 stub 的任何修改都会在你使用 Artisan 的 `make` 命令生成相应类时生效。

## 事件（Events）

在运行命令时，Artisan 会触发三个事件：
-   `Illuminate\Console\Events\ArtisanStarting`
-   `Illuminate\Console\Events\CommandStarting`
-   `Illuminate\Console\Events\CommandFinished`

`ArtisanStarting` 事件在 Artisan 开始运行时立即触发；
`CommandStarting` 事件在命令运行前立即触发；
`CommandFinished` 事件在命令执行完毕后触发。
