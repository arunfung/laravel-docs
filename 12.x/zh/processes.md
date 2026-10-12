
# 进程管理

- [简介](#introduction)
- [调用进程](#invoking-processes)
    - [进程选项](#process-options)
    - [进程输出](#process-output)
    - [管道](#process-pipelines)
- [异步进程](#asynchronous-processes)
    - [进程ID与信号](#process-ids-and-signals)
    - [异步进程输出](#asynchronous-process-output)
    - [异步进程超时](#asynchronous-process-timeouts)
- [并发进程](#concurrent-processes)
    - [命名进程池](#naming-pool-processes)
    - [进程池ID与信号](#pool-process-ids-and-signals)
- [测试](#testing)
    - [模拟进程](#faking-processes)
    - [模拟特定进程](#faking-specific-processes)
    - [模拟进程序列](#faking-process-sequences)
    - [模拟异步进程生命周期](#faking-asynchronous-process-lifecycles)
    - [可用断言](#available-assertions)
    - [防止游离进程](#preventing-stray-processes)

<a name="introduction"></a>
## 简介

Laravel 基于 [Symfony Process 组件](https://symfony.com/doc/current/components/process.html)提供了一套简洁而富有表现力的 API，让您能够方便地从 Laravel 应用中调用外部进程。Laravel 的进程管理功能专注于最常见的用例，并提供出色的开发者体验。

<a name="invoking-processes"></a>
## 调用进程

要调用一个进程，您可以使用 `Process` 门面提供的 `run` 和 `start`  方法。 `run`  方法会调用进程并等待其执行完成，而 `start` 方法用于异步进程执行。我们将在这篇文档中探讨这两种方式。首先，让我们看看如何调用一个基本的同步进程并检查其结果：

```php
use Illuminate\Support\Facades\Process;

$result = Process::run('ls -la');

return $result->output();
```

当然，`run` 方法返回的 `Illuminate\Contracts\Process\ProcessResult` 实例提供了多种有用的方法来检查进程结果：

```php
$result = Process::run('ls -la');

$result->successful();
$result->failed();
$result->exitCode();
$result->output();
$result->errorOutput();
```



<a name="throwing-exceptions"></a>
#### 异常处理

当进程执行结果返回非零退出码（表示执行失败）时，您可以使用 `throw` 和 `throwIf` 方法抛出 `Illuminate\Process\Exceptions\ProcessFailedException`异常。若进程执行成功，则会返回进程结果实例：

```php
$result = Process::run('ls -la')->throw();

$result = Process::run('ls -la')->throwIf($condition);
```

<a name="process-options"></a>
### 进程选项

当然，在调用进程之前，您可能需要自定义进程的行为。值得庆幸的是，Laravel允许您调整各种进程功能，如工作目录、超时和环境变量。

<a name="working-directory-path"></a>
#### 工作目录

使用 `path` 方法指定进程的工作目录。若不调用此方法，进程将继承当前 PHP 脚本的工作目录：

```php
$result = Process::path(__DIR__)->run('ls -la');
```

<a name="input"></a>
#### 标准输入

通过 `input` 方法为进程提供标准输入：

```php
$result = Process::input('Hello World')->run('cat');
```

<a name="timeouts"></a>
#### 超时设置

默认情况下，进程执行超过60秒会抛出 `Illuminate\Process\Exceptions\ProcessTimedOutException` 。可通过 `timeout` 方法自定义超时时间：

```php
$result = Process::timeout(120)->run('bash import.sh');
```

若要完全禁用超时限制，可使用 `forever` 方法：

```php
$result = Process::forever()->run('bash import.sh');
```



### `idleTimeout` 方法

`idleTimeout` 方法用于指定进程在未产生任何输出时的最大运行秒数：

```php
$result = Process::timeout(60)->idleTimeout(30)->run('bash import.sh');
```

#### 环境变量 (Environment Variables)

可以通过 `env` 方法为进程提供环境变量。调用的进程也会继承系统中定义的所有环境变量：

```php
$result = Process::forever()
    ->env(['IMPORT_PATH' => __DIR__])
    ->run('bash import.sh');
```

如果希望从调用的进程中移除继承的环境变量，可以将该环境变量设置为 `false`：


```php
$result = Process::forever()
    ->env(['LOAD_PATH' => false])
    ->run('bash import.sh');
```

#### TTY 模式

`tty` 方法可用于为进程启用 TTY 模式。TTY 模式会将进程的输入输出连接到你程序的输入输出，从而允许进程打开像 Vim 或 Nano 这样的编辑器：

```php
Process::forever()->tty()->run('vim');
```

### 进程输出 (Process Output)

如前所述，可以通过进程结果的 `output`（标准输出）和 `errorOutput`（标准错误输出）方法获取输出：

```php
use Illuminate\Support\Facades\Process;

$result = Process::run('ls -la');

echo $result->output();
echo $result->errorOutput();
```

此外，还可以通过向 `run` 方法传递闭包来实时收集输出。闭包会接收两个参数：输出类型（`stdout` 或 `stderr`）和输出字符串本身：

```php
$result = Process::run('ls -la', function (string $type, string $output) {
    echo $output;
});
```



Laravel 还提供了 `seeInOutput` 和 `seeInErrorOutput` 方法，可以方便地判断某个字符串是否包含在进程输出中：

```php
if (Process::run('ls -la')->seeInOutput('laravel')) {
    // ...
}
```

#### 禁用进程输出 (Disabling Process Output)

如果你的进程会生成大量你不关心的输出，可以通过完全禁用输出获取来节省内存。为此，在构建进程时调用 `quietly` 方法：

```php
use Illuminate\Support\Facades\Process;

$result = Process::quietly()->run('bash import.sh');
```

### 管道 (Pipelines)

有时你可能希望将一个进程的输出作为另一个进程的输入，这通常称为 **“管道”**。`Process` facade 提供的 `pipe` 方法可以轻松实现这一点。`pipe` 方法会同步执行管道中的各个进程，并返回管道中最后一个进程的结果：

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

如果不需要自定义管道中每个进程的配置，你也可以直接向 `pipe` 方法传递命令字符串数组：

```php
$result = Process::pipe([
    'cat example.txt',
    'grep -i "laravel"',
]);
```

通过向 `pipe` 方法传递闭包作为第二个参数，可以实时获取进程输出。闭包会接收两个参数：输出类型（`stdout` 或 `stderr`）和输出字符串本身：

```php
$result = Process::pipe(function (Pipe $pipe) {
    $pipe->command('cat example.txt');
    $pipe->command('grep -i "laravel"');
}, function (string $type, string $output) {
    echo $output;
});
```



Laravel 还允许你通过 `as` 方法为管道中的每个进程分配字符串键。这个键也会传递给 `pipe` 方法的输出闭包，从而可以确定输出属于哪个进程：

```php
$result = Process::pipe(function (Pipe $pipe) {
    $pipe->as('first')->command('cat example.txt');
    $pipe->as('second')->command('grep -i "laravel"');
})->start(function (string $type, string $output, string $key) {
    // ...
});
```

## 异步进程 (Asynchronous Processes)

虽然 `run` 方法会同步调用进程，但 `start` 方法可以用于异步调用进程。这样应用程序可以在进程后台运行时继续执行其他任务。调用后，可以使用 `running` 方法判断进程是否仍在运行：

```php
$process = Process::timeout(120)->start('bash import.sh');

while ($process->running()) {
    // ...
}

$result = $process->wait();
```

如上例所示，你可以调用 `wait` 方法等待进程执行完成，并获取进程结果实例：

```php
$process = Process::timeout(120)->start('bash import.sh');

// ...

$result = $process->wait();
```

### 进程 ID 与信号 (Process IDs and Signals)

`id` 方法可用于获取操作系统分配的运行进程 ID：

```php
$process = Process::start('bash import.sh');

return $process->id();
```

`signal` 方法可用于向运行中的进程发送信号。预定义的信号常量可参考 [PHP 文档](https://www.php.net/manual/en/pcntl.constants.php)：

```php
$process->signal(SIGUSR2);
```



### 异步进程输出 (Asynchronous Process Output)

当异步进程运行时，你可以通过 `output` 和 `errorOutput` 方法获取进程的完整当前输出；
但是，如果只想获取自上次读取以来的新输出，可以使用 `latestOutput` 和 `latestErrorOutput`：

```php
$process = Process::timeout(120)->start('bash import.sh');

while ($process->running()) {
    echo $process->latestOutput();
    echo $process->latestErrorOutput();

    sleep(1);
}
```

像 `run` 方法一样，也可以通过向 `start` 方法传递闭包实时收集异步进程输出。闭包会接收两个参数：输出类型（`stdout` 或 `stderr`）和输出字符串本身：

```php
$process = Process::start('bash import.sh', function (string $type, string $output) {
    echo $output;
});

$result = $process->wait();
```

你也可以不必等进程执行完成，通过 `waitUntil` 方法基于进程输出停止等待。当传入的闭包返回 `true` 时，Laravel 会停止等待进程完成：

```php
$process = Process::start('bash import.sh');

$process->waitUntil(function (string $type, string $output) {
    return $output === 'Ready...';
});
```

### 异步进程超时 (Asynchronous Process Timeouts)

在异步进程运行期间，可以使用 `ensureNotTimedOut` 方法检查进程是否已超时。如果进程超时，该方法会抛出一个 [超时异常](#timeouts)：

```php
$process = Process::timeout(120)->start('bash import.sh');

while ($process->running()) {
    $process->ensureNotTimedOut();

    // ...

    sleep(1);
}
```



## 并发进程（Concurrent Processes）

Laravel 还可以轻松管理一组并发的异步进程，使你能够同时执行多个任务。要开始使用，请调用 `pool` 方法，该方法接受一个闭包，并将 `Illuminate\Process\Pool` 实例传入闭包中。

在闭包中，你可以定义属于该进程池的进程。一旦通过 `start` 方法启动进程池，你可以通过 `running` 方法访问正在运行的进程集合（[集合](/docs/laravel/12.x/collections)）：

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

如你所见，你可以等待进程池中的所有进程执行完成，并通过 `wait` 方法获取它们的结果。`wait` 方法返回一个可访问数组对象，你可以通过键访问进程池中每个进程的结果实例：

```php
$results = $pool->wait();

echo $results[0]->output();
```

或者，为了更方便使用，你可以使用 `concurrently` 方法启动一个异步进程池，并立即等待其结果。当结合 PHP 的数组解构语法时，这种用法特别简洁：

```php
[$first, $second, $third] = Process::concurrently(function (Pool $pool) {
    $pool->path(__DIR__)->command('ls -la');
    $pool->path(app_path())->command('ls -la');
    $pool->path(storage_path())->command('ls -la');
});

echo $first->output();
```



### 为进程池命名

通过数字键访问进程池的结果可读性不高；因此，Laravel 允许你通过 `as` 方法为池中的每个进程分配字符串键。这个键也会传递给 `start` 方法提供的闭包，从而可以确定输出属于哪个进程：

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

### 进程池的进程 ID 与信号

由于进程池的 `running` 方法提供了池中所有已调用进程的集合，你可以轻松访问底层进程的 ID：

```php
$processIds = $pool->running()->each->id();
```

另外，为了方便，你可以在进程池上调用 `signal` 方法向池中每个进程发送信号：

```php
$pool->signal(SIGUSR2);
```

## 测试

许多 Laravel 服务都提供了便捷的功能来轻松、清晰地编写测试，进程服务也不例外。`Process` facade 的 `fake` 方法允许你在调用进程时返回模拟 / 虚拟结果。

### 模拟进程

为了演示 Laravel 模拟进程的能力，假设有一个路由会调用一个进程：

```php
use Illuminate\Support\Facades\Process;
use Illuminate\Support\Facades\Route;

Route::get('/import', function () {
    Process::run('bash import.sh');

    return 'Import complete!';
});
```



在测试该路由时，我们可以通过在 `Process` facade 上调用 `fake` 方法（不传递任何参数）来指示 Laravel 为每个调用的进程返回一个虚拟的、成功的结果。此外，我们还可以[断言](#available-assertions) 某个进程确实被“运行”过：

```php tab=Pest
<?php

use Illuminate\Process\PendingProcess;
use Illuminate\Contracts\Process\ProcessResult;
use Illuminate\Support\Facades\Process;

test('process is invoked', function () {
    Process::fake();

    $response = $this->get('/import');

    // 简单的进程断言...
    Process::assertRan('bash import.sh');

    // 或者检查进程配置...
    Process::assertRan(function (PendingProcess $process, ProcessResult $result) {
        return $process->command === 'bash import.sh' &&
               $process->timeout === 60;
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Process\PendingProcess;
use Illuminate\Contracts\Process\ProcessResult;
use Illuminate\Support\Facades\Process;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_process_is_invoked(): void
    {
        Process::fake();

        $response = $this->get('/import');

        // 简单的进程断言...
        Process::assertRan('bash import.sh');

        // 或者检查进程配置...
        Process::assertRan(function (PendingProcess $process, ProcessResult $result) {
            return $process->command === 'bash import.sh' &&
                   $process->timeout === 60;
        });
    }
}
```

如前所述，在 `Process` facade 上调用 `fake` 方法会指示 Laravel 总是返回一个成功的、无输出的进程结果。但你可以轻松通过 `Process` facade 的 `result` 方法为虚拟进程指定输出和退出码：

```php
Process::fake([
    '*' => Process::result(
        output: 'Test output',
        errorOutput: 'Test error output',
        exitCode: 1,
    ),
]);
```

### 针对特定进程进行模拟

如你在前面的示例中看到的，`Process` facade 允许你通过向 `fake` 方法传递一个数组，为不同的进程指定不同的虚拟结果。




数组的键应该表示你希望模拟的命令模式，以及与之关联的结果。`*` 字符可以用作通配符。任何未被模拟的进程命令将会被实际执行。你可以使用 `Process` facade 的 `result` 方法来构建这些命令的虚拟结果：

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

如果你不需要自定义虚拟进程的退出码或错误输出，直接用字符串指定虚拟结果会更方便：

```php
Process::fake([
    'cat *' => 'Test "cat" output',
    'ls *' => 'Test "ls" output',
]);
```

### 模拟进程序列

如果你测试的代码多次调用相同命令的进程，你可能希望为每次调用分配不同的虚拟结果。可以通过 `Process` facade 的 `sequence` 方法实现：

```php
Process::fake([
    'ls *' => Process::sequence()
        ->push(Process::result('First invocation'))
        ->push(Process::result('Second invocation')),
]);
```

### 模拟异步进程生命周期

到目前为止，我们主要讨论了通过 `run` 方法同步调用的虚拟进程。但如果你测试的代码与通过 `start` 异步调用的进程交互，你可能需要更复杂的方式来描述虚拟进程。

例如，假设以下路由与异步进程交互：

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



为了正确模拟这个异步进程，我们需要描述 `running` 方法返回 `true` 的次数。此外，我们可能希望指定多行输出按顺序返回。可以使用 `Process` facade 的 `describe` 方法来实现：

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

上面的示例说明如下：
-   使用 `output` 和 `errorOutput` 方法，可以指定多行输出，按顺序返回。
-   `exitCode` 方法用于指定虚拟进程的最终退出码。
-   `iterations` 方法用于指定 `running` 方法应返回 `true` 的次数。

### 可用断言

如前所述，Laravel 为功能测试提供了多种进程断言方法。下面介绍其中的一些。

#### assertRan

断言某个进程已被调用：

```php
use Illuminate\Support\Facades\Process;

Process::assertRan('ls -la');
```

`assertRan` 方法也可以接受一个闭包，闭包会接收进程实例和进程结果实例，你可以检查进程的配置选项。如果闭包返回 `true`，断言即为通过：

```php
Process::assertRan(fn ($process, $result) =>
    $process->command === 'ls -la' &&
    $process->path === __DIR__ &&
    $process->timeout === 60
);
```

-   `$process` 是 `Illuminate\Process\PendingProcess` 的实例
-   `$result` 是 `Illuminate\Contracts\Process\ProcessResult` 的实例




#### 断言未运行（assertDidntRun）

断言某个进程没有被调用：

```php
use Illuminate\Support\Facades\Process;

Process::assertDidntRun('ls -la');
```

和 `assertRan` 方法类似，`assertDidntRun` 方法也可以接受一个闭包，该闭包会接收进程实例和进程结果实例，让你检查进程的配置选项。如果闭包返回 `true`，断言将“失败”：

```php
Process::assertDidntRun(fn (PendingProcess $process, ProcessResult $result) =>
    $process->command === 'ls -la'
);
```

#### 断言运行次数（assertRanTimes）

断言某个进程被调用了指定次数：

```php
use Illuminate\Support\Facades\Process;

Process::assertRanTimes('ls -la', times: 3);
```

`assertRanTimes` 方法也可以接受一个闭包，该闭包会接收进程实例和进程结果实例，让你检查进程的配置选项。如果闭包返回 `true` 且进程被调用了指定次数，断言将“通过”：

```php
Process::assertRanTimes(function (PendingProcess $process, ProcessResult $result) {
    return $process->command === 'ls -la';
}, times: 3);
```

### 防止未模拟进程（Preventing Stray Processes）

如果你希望确保在单个测试或整个测试套件中，所有调用的进程都有被模拟，可以调用 `preventStrayProcesses` 方法。调用此方法后，任何没有对应模拟结果的进程都会抛出异常，而不会启动实际进程：

```php
use Illuminate\Support\Facades\Process;

Process::preventStrayProcesses();

Process::fake([
    'ls *' => 'Test output...',
]);

// Fake response is returned...
Process::run('ls -la');

// An exception is thrown...
Process::run('bash import.sh');
```
