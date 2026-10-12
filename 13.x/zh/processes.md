# 进程管理

- [简介](#introduction)
- [调用进程](#invoking-processes)
    - [进程选项](#process-options)
    - [进程输出](#process-output)
    - [管道](#process-pipelines)
- [异步进程](#asynchronous-processes)
    - [进程 ID 与信号](#process-ids-and-signals)
    - [异步进程输出](#asynchronous-process-output)
    - [异步进程超时](#asynchronous-process-timeouts)
- [并发进程](#concurrent-processes)
    - [为进程池中的进程命名](#naming-pool-processes)
    - [进程池中的进程 ID 与信号](#pool-process-ids-and-signals)
- [测试](#testing)
    - [模拟进程](#faking-processes)
    - [模拟特定进程](#faking-specific-processes)
    - [模拟进程序列](#faking-process-sequences)
    - [模拟异步进程生命周期](#faking-asynchronous-process-lifecycles)
    - [可用断言](#available-assertions)
    - [防止未模拟的进程运行](#preventing-stray-processes)

<a name="introduction"></a>
## 简介

Laravel 基于 [Symfony Process 组件](https://symfony.com/doc/current/components/process.html)提供了一套简洁而富有表现力的 API，让你能够方便地从 Laravel 应用中调用外部进程。Laravel 的进程管理功能专注于最常见的用例，并提供出色的开发者体验。

<a name="invoking-processes"></a>
## 调用进程

要调用一个进程，你可以使用 `Process` 门面提供的 `run` 和 `start` 方法。`run` 方法会调用进程并等待其执行完成，而 `start` 方法用于异步执行进程。本文将介绍这两种方式。首先，让我们看看如何调用一个基本的同步进程并检查其结果：

```php
use Illuminate\Support\Facades\Process;

$result = Process::run('ls -la');

return $result->output();
```

当然，`run` 方法返回的 `Illuminate\Contracts\Process\ProcessResult` 实例提供了多种有用的方法来检查进程结果：

```php
$result = Process::run('ls -la');

$result->command();
$result->successful();
$result->failed();
$result->output();
$result->errorOutput();
$result->exitCode();
```

<a name="throwing-exceptions"></a>
#### 抛出异常

拿到进程结果后，如果你希望在退出码大于零（表示执行失败）时抛出 `Illuminate\Process\Exceptions\ProcessFailedException` 异常，可以使用 `throw` 和 `throwIf` 方法。如果进程没有失败，则会返回 `ProcessResult` 实例：

```php
$result = Process::run('ls -la')->throw();

$result = Process::run('ls -la')->throwIf($condition);
```

<a name="process-options"></a>
### 进程选项

当然，在调用进程之前，你可能需要自定义进程的行为。Laravel 允许你调整各种进程选项，如工作目录、超时和环境变量。

<a name="working-directory-path"></a>
#### 工作目录路径

你可以使用 `path` 方法指定进程的工作目录。如果不调用此方法，进程将继承当前执行的 PHP 脚本的工作目录：

```php
$result = Process::path(__DIR__)->run('ls -la');
```

<a name="input"></a>
#### 输入

你可以使用 `input` 方法通过进程的「标准输入」提供输入内容：

```php
$result = Process::input('Hello World')->run('cat');
```

<a name="timeouts"></a>
#### 超时

默认情况下，进程执行超过 60 秒后会抛出 `Illuminate\Process\Exceptions\ProcessTimedOutException` 异常。不过，你可以通过 `timeout` 方法自定义超时时间：

```php
$result = Process::timeout(120)->run('bash import.sh');
```

`timeout` 和 `idleTimeout` 方法也接受 `CarbonInterval` 实例：

```php
use function Illuminate\Support\minutes;

$result = Process::timeout(minutes(2))->run('bash import.sh');
```

如果你希望完全禁用进程的超时限制，可以调用 `forever` 方法：

```php
$result = Process::forever()->run('bash import.sh');
```

`idleTimeout` 方法可用于指定进程在未产生任何输出时的最长运行秒数：

```php
$result = Process::timeout(60)->idleTimeout(30)->run('bash import.sh');
```

<a name="environment-variables"></a>
#### 环境变量

你可以通过 `env` 方法为进程提供环境变量。调用的进程也会继承系统中定义的所有环境变量：

```php
$result = Process::forever()
    ->env(['IMPORT_PATH' => __DIR__])
    ->run('bash import.sh');
```

如果你希望从调用的进程中移除某个继承的环境变量，可以将该环境变量的值设置为 `false`：

```php
$result = Process::forever()
    ->env(['LOAD_PATH' => false])
    ->run('bash import.sh');
```

<a name="tty-mode"></a>
#### TTY 模式

`tty` 方法可用于为进程启用 TTY 模式。TTY 模式会将进程的输入输出连接到你程序的输入输出，从而允许进程打开 Vim 或 Nano 这样的编辑器：

```php
Process::forever()->tty()->run('vim');
```

> [!WARNING]
> Windows 不支持 TTY 模式。

<a name="process-output"></a>
### 进程输出

如前所述，你可以通过进程结果的 `output`（标准输出）和 `errorOutput`（标准错误输出）方法获取进程输出：

```php
use Illuminate\Support\Facades\Process;

$result = Process::run('ls -la');

echo $result->output();
echo $result->errorOutput();
```

此外，你还可以将闭包作为第二个参数传递给 `run` 方法，以实时收集输出。闭包会接收两个参数：输出类型（`stdout` 或 `stderr`）和输出字符串本身：

```php
$result = Process::run('ls -la', function (string $type, string $output) {
    echo $output;
});
```

Laravel 还提供了 `seeInOutput` 和 `seeInErrorOutput` 方法，可以方便地判断进程输出中是否包含指定字符串：

```php
if (Process::run('ls -la')->seeInOutput('laravel')) {
    // ...
}
```

<a name="disabling-process-output"></a>
#### 禁用进程输出

如果进程会产生大量你不关心的输出，可以完全禁用输出获取以节省内存。为此，在构建进程时调用 `quietly` 方法：

```php
use Illuminate\Support\Facades\Process;

$result = Process::quietly()->run('bash import.sh');
```

<a name="process-pipelines"></a>
### 管道

有时你可能希望将一个进程的输出作为另一个进程的输入，这通常称为通过「管道」传递进程输出。`Process` 门面提供的 `pipe` 方法可以轻松实现这一点。`pipe` 方法会同步执行管道中的各个进程，并返回管道中最后一个进程的结果：

```php
use Illuminate\Process\Pipe;
use Illuminate\Support\Facades\Process;

$result = Process::pipe(function (Pipe $pipe) {
    $pipe->command('cat example.txt');
    $pipe->command('grep -i "laravel"');
});

if ($result->successful()) {
    // ...
}
```

如果不需要自定义管道中各个进程的配置，你可以直接向 `pipe` 方法传递命令字符串数组：

```php
$result = Process::pipe([
    'cat example.txt',
    'grep -i "laravel"',
]);
```

将闭包作为第二个参数传递给 `pipe` 方法，可以实时收集进程输出。闭包会接收两个参数：输出类型（`stdout` 或 `stderr`）和输出字符串本身：

```php
$result = Process::pipe(function (Pipe $pipe) {
    $pipe->command('cat example.txt');
    $pipe->command('grep -i "laravel"');
}, function (string $type, string $output) {
    echo $output;
});
```

Laravel 还允许你通过 `as` 方法为管道中的每个进程分配字符串键。这个键也会传递给 `pipe` 方法的输出闭包，从而让你确定输出属于哪个进程：

```php
$result = Process::pipe(function (Pipe $pipe) {
    $pipe->as('first')->command('cat example.txt');
    $pipe->as('second')->command('grep -i "laravel"');
}, function (string $type, string $output, string $key) {
    // ...
});
```

<a name="asynchronous-processes"></a>
## 异步进程

`run` 方法会同步调用进程，而 `start` 方法可用于异步调用进程。这样，应用就能在进程后台运行时继续执行其他任务。调用进程后，你可以使用 `running` 方法判断进程是否仍在运行：

```php
$process = Process::timeout(120)->start('bash import.sh');

while ($process->running()) {
    // ...
}

$result = $process->wait();
```

如上例所示，你可以调用 `wait` 方法等待进程执行完成，并获取 `ProcessResult` 实例：

```php
$process = Process::timeout(120)->start('bash import.sh');

// ...

$result = $process->wait();
```

<a name="process-ids-and-signals"></a>
### 进程 ID 与信号

`id` 方法可用于获取操作系统为运行中的进程分配的进程 ID：

```php
$process = Process::start('bash import.sh');

return $process->id();
```

你可以使用 `signal` 方法向运行中的进程发送「信号」。预定义的信号常量列表可在 [PHP 文档](https://www.php.net/manual/en/pcntl.constants.php)中找到：

```php
$process->signal(SIGUSR2);
```

<a name="asynchronous-process-output"></a>
### 异步进程输出

当异步进程运行时，你可以使用 `output` 和 `errorOutput` 方法获取进程当前的全部输出；如果只想获取自上次读取以来产生的新输出，可以使用 `latestOutput` 和 `latestErrorOutput` 方法：

```php
$process = Process::timeout(120)->start('bash import.sh');

while ($process->running()) {
    echo $process->latestOutput();
    echo $process->latestErrorOutput();

    sleep(1);
}
```

与 `run` 方法一样，你也可以将闭包作为第二个参数传递给 `start` 方法，以实时收集异步进程的输出。闭包会接收两个参数：输出类型（`stdout` 或 `stderr`）和输出字符串本身：

```php
$process = Process::start('bash import.sh', function (string $type, string $output) {
    echo $output;
});

$result = $process->wait();
```

你可以使用 `waitUntil` 方法根据进程输出停止等待，而不必一直等到进程执行完成。当传递给 `waitUntil` 方法的闭包返回 `true` 时，Laravel 就会停止等待进程完成：

```php
$process = Process::start('bash import.sh');

$process->waitUntil(function (string $type, string $output) {
    return $output === 'Ready...';
});
```

<a name="asynchronous-process-timeouts"></a>
### 异步进程超时

在异步进程运行期间，你可以使用 `ensureNotTimedOut` 方法检查进程是否已超时。如果进程超时，该方法会抛出[超时异常](#timeouts)：

```php
$process = Process::timeout(120)->start('bash import.sh');

while ($process->running()) {
    $process->ensureNotTimedOut();

    // ...

    sleep(1);
}
```

<a name="concurrent-processes"></a>
## 并发进程

Laravel 还可以轻松管理一组并发的异步进程，让你同时执行多个任务。要开始使用，请调用 `pool` 方法，该方法接受一个闭包，并将 `Illuminate\Process\Pool` 实例传入闭包中。

在闭包中，你可以定义属于该进程池的进程。通过 `start` 方法启动进程池后，你可以使用 `running` 方法获取正在运行的进程[集合](/docs/{{version}}/collections)：

```php
use Illuminate\Process\Pool;
use Illuminate\Support\Facades\Process;

$pool = Process::pool(function (Pool $pool) {
    $pool->path(__DIR__)->command('bash import-1.sh');
    $pool->path(__DIR__)->command('bash import-2.sh');
    $pool->path(__DIR__)->command('bash import-3.sh');
})->start(function (string $type, string $output, int $key) {
    // ...
});

while ($pool->running()->isNotEmpty()) {
    // ...
}

$results = $pool->wait();
```

如你所见，你可以通过 `wait` 方法等待进程池中的所有进程执行完成并获取它们的结果。`wait` 方法返回一个支持数组访问的对象，让你能够通过键访问进程池中每个进程的 `ProcessResult` 实例：

```php
$results = $pool->wait();

echo $results[0]->output();
```

为了更方便地使用，你也可以通过 `concurrently` 方法启动一个异步进程池，并立即等待其结果。结合 PHP 的数组解构功能，这种写法会更加简洁直观：

```php
[$first, $second, $third] = Process::concurrently(function (Pool $pool) {
    $pool->path(__DIR__)->command('ls -la');
    $pool->path(app_path())->command('ls -la');
    $pool->path(storage_path())->command('ls -la');
});

echo $first->output();
```

<a name="naming-pool-processes"></a>
### 为进程池中的进程命名

通过数字键访问进程池的结果不够直观，因此 Laravel 允许你通过 `as` 方法为池中的每个进程分配字符串键。这个键也会传递给 `start` 方法的闭包，从而让你确定输出属于哪个进程：

```php
$pool = Process::pool(function (Pool $pool) {
    $pool->as('first')->command('bash import-1.sh');
    $pool->as('second')->command('bash import-2.sh');
    $pool->as('third')->command('bash import-3.sh');
})->start(function (string $type, string $output, string $key) {
    // ...
});

$results = $pool->wait();

return $results['first']->output();
```

<a name="pool-process-ids-and-signals"></a>
### 进程池中的进程 ID 与信号

进程池的 `running` 方法会返回池中所有已调用进程的集合，因此你可以轻松获取这些底层进程的 ID：

```php
$processIds = $pool->running()->map->id();
```

此外，你可以直接在进程池上调用 `signal` 方法，向池中的每个进程发送信号：

```php
$pool->signal(SIGUSR2);
```

<a name="testing"></a>
## 测试

许多 Laravel 服务都提供了便捷的功能，让你能够轻松、清晰地编写测试，进程服务也不例外。`Process` 门面的 `fake` 方法允许你指示 Laravel 在调用进程时返回桩结果或模拟结果。

<a name="faking-processes"></a>
### 模拟进程

为了了解 Laravel 模拟进程的能力，假设有一个调用进程的路由：

```php
use Illuminate\Support\Facades\Process;
use Illuminate\Support\Facades\Route;

Route::get('/import', function () {
    Process::run('bash import.sh');

    return 'Import complete!';
});
```

测试该路由时，我们可以在 `Process` 门面上调用 `fake` 方法，不传递任何参数，以指示 Laravel 为每个调用的进程返回一个模拟的成功结果。此外，我们还可以[断言](#available-assertions)某个进程确实被「运行」过：

```php tab=Pest
<?php

use Illuminate\Contracts\Process\ProcessResult;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;

test('process is invoked', function () {
    Process::fake();

    $response = $this->get('/import');

    // 简单的进程断言……
    Process::assertRan('bash import.sh');

    // 或者，检查进程配置……
    Process::assertRan(function (PendingProcess $process, ProcessResult $result) {
        return $process->command === 'bash import.sh' &&
               $process->timeout === 60;
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Contracts\Process\ProcessResult;
use Illuminate\Process\PendingProcess;
use Illuminate\Support\Facades\Process;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_process_is_invoked(): void
    {
        Process::fake();

        $response = $this->get('/import');

        // 简单的进程断言……
        Process::assertRan('bash import.sh');

        // 或者，检查进程配置……
        Process::assertRan(function (PendingProcess $process, ProcessResult $result) {
            return $process->command === 'bash import.sh' &&
                   $process->timeout === 60;
        });
    }
}
```

如前所述，在 `Process` 门面上调用 `fake` 方法，会指示 Laravel 始终返回一个无输出的成功进程结果。不过，你可以通过 `Process` 门面的 `result` 方法，轻松为模拟进程指定输出和退出码：

```php
Process::fake([
    '*' => Process::result(
        output: 'Test output',
        errorOutput: 'Test error output',
        exitCode: 1,
    ),
]);
```

<a name="faking-specific-processes"></a>
### 模拟特定进程

如前面的示例所示，`Process` 门面允许你通过向 `fake` 方法传递数组，为不同的进程指定不同的模拟结果。

数组的键应表示你希望模拟的命令模式，对应的值则是这些命令的模拟结果。`*` 字符可以用作通配符。任何未被模拟的进程命令都会实际执行。你可以使用 `Process` 门面的 `result` 方法为这些命令构建桩结果或模拟结果：

```php
Process::fake([
    'cat *' => Process::result(
        output: 'Test "cat" output',
    ),
    'ls *' => Process::result(
        output: 'Test "ls" output',
    ),
]);
```

如果不需要自定义模拟进程的退出码或错误输出，直接用字符串指定模拟进程的结果会更方便：

```php
Process::fake([
    'cat *' => 'Test "cat" output',
    'ls *' => 'Test "ls" output',
]);
```

<a name="faking-process-sequences"></a>
### 模拟进程序列

如果被测试的代码多次调用使用相同命令的进程，你可能希望为每次调用分配不同的模拟进程结果。可以通过 `Process` 门面的 `sequence` 方法实现这一点：

```php
Process::fake([
    'ls *' => Process::sequence()
        ->push(Process::result('First invocation'))
        ->push(Process::result('Second invocation')),
]);
```

<a name="faking-asynchronous-process-lifecycles"></a>
### 模拟异步进程生命周期

到目前为止，我们主要讨论了如何模拟通过 `run` 方法同步调用的进程。如果被测试的代码需要与通过 `start` 方法调用的异步进程交互，你可能需要更细致地描述模拟进程。

例如，假设有以下与异步进程交互的路由：

```php
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Route;

Route::get('/import', function () {
    $process = Process::start('bash import.sh');

    while ($process->running()) {
        Log::info($process->latestOutput());
        Log::info($process->latestErrorOutput());
    }

    return 'Done';
});
```

为了正确模拟这个进程，我们需要描述 `running` 方法应返回 `true` 的次数。此外，我们可能希望指定多行按顺序返回的输出。可以使用 `Process` 门面的 `describe` 方法实现这一点：

```php
Process::fake([
    'bash import.sh' => Process::describe()
        ->output('First line of standard output')
        ->errorOutput('First line of error output')
        ->output('Second line of standard output')
        ->exitCode(0)
        ->iterations(3),
]);
```

让我们仔细看看上面的示例。使用 `output` 和 `errorOutput` 方法，可以指定多行按顺序返回的输出。`exitCode` 方法可用于指定模拟进程的最终退出码。最后，`iterations` 方法可用于指定 `running` 方法应返回 `true` 的次数。

<a name="available-assertions"></a>
### 可用断言

如[前文所述](#faking-processes)，Laravel 为功能测试提供了多种进程断言。下面将逐一介绍这些断言。

<a name="assert-process-ran"></a>
#### assertRan

断言某个进程已被调用：

```php
use Illuminate\Support\Facades\Process;

Process::assertRan('ls -la');
```

如果调用进程时使用了参数数组，你可以将相同的数组传递给断言：

```php
Process::assertRan(['php', 'artisan', 'migrate']);
```

`assertRanTimes` 和 `assertDidntRun` 方法也接受数组形式的命令。

`assertRan` 方法也接受一个闭包，闭包会接收进程实例和进程结果实例，让你能够检查进程的配置选项。如果闭包返回 `true`，断言就会「通过」：

```php
Process::assertRan(fn ($process, $result) =>
    $process->command === 'ls -la' &&
    $process->path === __DIR__ &&
    $process->timeout === 60
);
```

传递给 `assertRan` 闭包的 `$process` 是 `Illuminate\Process\PendingProcess` 实例，而 `$result` 是 `Illuminate\Contracts\Process\ProcessResult` 实例。

<a name="assert-process-didnt-run"></a>
#### assertDidntRun

断言某个进程未被调用：

```php
use Illuminate\Support\Facades\Process;

Process::assertDidntRun('ls -la');
```

与 `assertRan` 方法类似，`assertDidntRun` 方法也接受一个闭包，闭包会接收进程实例和进程结果实例，让你能够检查进程的配置选项。如果闭包返回 `true`，断言就会「失败」：

```php
Process::assertDidntRun(fn (PendingProcess $process, ProcessResult $result) =>
    $process->command === 'ls -la'
);
```

<a name="assert-process-ran-times"></a>
#### assertRanTimes

断言某个进程被调用了指定次数：

```php
use Illuminate\Support\Facades\Process;

Process::assertRanTimes('ls -la', times: 3);
```

`assertRanTimes` 方法也接受一个闭包，闭包会接收 `PendingProcess` 和 `ProcessResult` 实例，让你能够检查进程的配置选项。如果闭包返回 `true`，且进程被调用了指定次数，断言就会「通过」：

```php
Process::assertRanTimes(function (PendingProcess $process, ProcessResult $result) {
    return $process->command === 'ls -la';
}, times: 3);
```

<a name="assert-processes-ran-in-order"></a>
#### assertRanInOrder

断言进程按指定顺序被调用：

```php
Process::assertRanInOrder([
    'git fetch',
    'composer install',
]);
```

与其他进程断言一样，`assertRanInOrder` 方法接受命令字符串、命令参数数组或闭包。

<a name="preventing-stray-processes"></a>
### 防止未模拟的进程运行

如果你希望确保在单个测试或整个测试套件中，所有调用的进程都已被模拟，可以调用 `preventStrayProcesses` 方法。调用此方法后，任何没有对应模拟结果的进程都会抛出异常，而不会启动实际进程：

```php
use Illuminate\Support\Facades\Process;

Process::preventStrayProcesses();

Process::fake([
    'ls *' => 'Test output...',
]);

// 返回模拟响应……
Process::run('ls -la');

// 抛出异常……
Process::run('bash import.sh');
```
