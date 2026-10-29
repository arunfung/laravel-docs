# Laravel Envoy

- [简介](#introduction)
- [安装](#installation)
- [编写任务](#writing-tasks)
    - [定义任务](#defining-tasks)
    - [多服务器](#multiple-servers)
    - [初始化](#setup)
    - [变量](#variables)
    - [故事](#stories)
    - [钩子](#completion-hooks)
- [运行任务](#running-tasks)
    - [确认任务执行](#confirming-task-execution)
- [通知](#notifications)
    - [Slack](#slack)
    - [Discord](#discord)
    - [Telegram](#telegram)
    - [Microsoft Teams](#microsoft-teams)

<a name="introduction"></a>
## 简介

[Laravel Envoy](https://github.com/laravel/envoy) 是一个用于在远程服务器上执行常见任务的工具。借助 [Blade](/docs/{{version}}/blade) 风格的语法，你可以轻松配置部署、运行 Artisan 命令等任务。目前，Envoy 仅支持 Mac 和 Linux 操作系统，不过也可以通过 [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install-win10) 在 Windows 上使用。

<a name="installation"></a>
## 安装

首先，使用 Composer 包管理器将 Envoy 安装到项目中：

```shell
composer require laravel/envoy --dev
```

安装 Envoy 后，你可以在应用的 `vendor/bin` 目录中找到 Envoy 可执行文件：

```shell
php vendor/bin/envoy
```

<a name="writing-tasks"></a>
## 编写任务

<a name="defining-tasks"></a>
### 定义任务

任务是 Envoy 的基本组成单元，定义了调用任务时应在远程服务器上执行的 shell 命令。例如，你可以定义一个任务，在应用的所有队列工作进程服务器上执行 `php artisan queue:restart` 命令。

所有 Envoy 任务都应定义在应用根目录的 `Envoy.blade.php` 文件中。下面是一个入门示例：

```blade
@servers(['web' => ['user@192.168.1.1'], 'workers' => ['user@192.168.1.2']])

@task('restart-queues', ['on' => 'workers'])
    cd /home/user/example.com
    php artisan queue:restart
@endtask
```

如你所见，文件顶部通过 `@servers` 定义了一个数组，这样就可以在任务声明中通过 `on` 选项引用这些服务器。`@servers` 声明必须始终写在同一行中。在 `@task` 声明内部，应填写调用任务时需要在服务器上执行的 shell 命令。

<a name="local-tasks"></a>
#### 本地任务

将服务器的 IP 地址指定为 `127.0.0.1`，即可强制脚本在本地计算机上运行：

```blade
@servers(['localhost' => '127.0.0.1'])
```

<a name="importing-envoy-tasks"></a>
#### 导入 Envoy 任务

使用 `@import` 指令，你可以导入其他 Envoy 文件，将其中的故事和任务添加到自己的文件中。导入后，就可以像调用自己 Envoy 文件中定义的任务一样执行这些任务：

```blade
@import('vendor/package/Envoy.blade.php')
```

<a name="multiple-servers"></a>
### 多服务器

Envoy 让你可以轻松地在多台服务器上运行任务。首先，在 `@servers` 声明中添加其他服务器，并为每台服务器指定唯一的名称。定义好这些服务器后，就可以在任务的 `on` 数组中列出它们：

```blade
@servers(['web-1' => '192.168.1.1', 'web-2' => '192.168.1.2'])

@task('deploy', ['on' => ['web-1', 'web-2']])
    cd /home/user/example.com
    git pull origin {{ $branch }}
    php artisan migrate --force
@endtask
```

<a name="parallel-execution"></a>
#### 并行执行

默认情况下，任务会在各台服务器上依次执行。也就是说，任务在第一台服务器上运行完毕后，才会开始在第二台服务器上执行。如果你希望在多台服务器上并行运行任务，可以在任务声明中添加 `parallel` 选项：

```blade
@servers(['web-1' => '192.168.1.1', 'web-2' => '192.168.1.2'])

@task('deploy', ['on' => ['web-1', 'web-2'], 'parallel' => true])
    cd /home/user/example.com
    git pull origin {{ $branch }}
    php artisan migrate --force
@endtask
```

<a name="setup"></a>
### 初始化

有时，你可能需要在运行 Envoy 任务前执行一些 PHP 代码。你可以使用 `@setup` 指令定义一个 PHP 代码块，使其在任务运行前执行：

```blade
@setup
    $now = new DateTime;
@endsetup
```

如果需要在任务执行前引入其他 PHP 文件，可以在 `Envoy.blade.php` 文件顶部使用 `@include` 指令：

```blade
@include('vendor/autoload.php')

@task('restart-queues')
    # ...
@endtask
```

<a name="variables"></a>
### 变量

如果需要，你可以在调用 Envoy 时通过命令行向任务传递参数：

```shell
php vendor/bin/envoy run deploy --branch=master
```

在任务中，你可以使用 Blade 的「输出」语法访问这些选项，也可以编写 Blade 的 `if` 语句和循环。例如，在执行 `git pull` 命令之前，先检查 `$branch` 变量是否存在：

```blade
@servers(['web' => ['user@192.168.1.1']])

@task('deploy', ['on' => 'web'])
    cd /home/user/example.com

    @if ($branch)
        git pull origin {{ $branch }}
    @endif

    php artisan migrate --force
@endtask
```

<a name="stories"></a>
### 故事

故事（Story）将一组任务归到一个便于调用的名称下。例如，你可以在 `deploy` 故事的定义中列出 `update-code` 和 `install-dependencies`，从而依次运行这两个任务：

```blade
@servers(['web' => ['user@192.168.1.1']])

@story('deploy')
    update-code
    install-dependencies
@endstory

@task('update-code')
    cd /home/user/example.com
    git pull origin master
@endtask

@task('install-dependencies')
    cd /home/user/example.com
    composer install
@endtask
```

编写好故事后，就可以像调用任务一样调用它：

```shell
php vendor/bin/envoy run deploy
```

<a name="completion-hooks"></a>
### 钩子

运行任务和故事时，会执行一系列钩子。Envoy 支持的钩子类型包括 `@before`、`@after`、`@error`、`@success` 和 `@finished`。这些钩子中的所有代码都会作为 PHP 代码解析并在本地执行，而非在任务所操作的远程服务器上执行。

你可以按需定义任意数量的各类钩子，它们会按照在 Envoy 脚本中出现的顺序执行。

<a name="hook-before"></a>
#### `@before`

每个任务执行之前，Envoy 脚本中注册的所有 `@before` 钩子都会执行。这些钩子会接收到即将执行的任务名称：

```blade
@before
    if ($task === 'deploy') {
        // ...
    }
@endbefore
```

<a name="completion-after"></a>
#### `@after`

每个任务执行之后，Envoy 脚本中注册的所有 `@after` 钩子都会执行。这些钩子会接收到刚刚执行的任务名称：

```blade
@after
    if ($task === 'deploy') {
        // ...
    }
@endafter
```

<a name="completion-error"></a>
#### `@error`

每次任务执行失败（退出状态码大于 `0`）后，Envoy 脚本中注册的所有 `@error` 钩子都会执行。这些钩子会接收到执行失败的任务名称：

```blade
@error
    if ($task === 'deploy') {
        // ...
    }
@enderror
```

<a name="completion-success"></a>
#### `@success`

如果所有任务都执行完毕且没有发生错误，Envoy 脚本中注册的所有 `@success` 钩子都会执行：

```blade
@success
    // ...
@endsuccess
```

<a name="completion-finished"></a>
#### `@finished`

所有任务执行结束后，无论退出状态如何，所有 `@finished` 钩子都会执行。这些钩子会接收到已完成任务的状态码，该值可能是 `null` 或大于等于 `0` 的整数（`integer`）：

```blade
@finished
    if ($exitCode > 0) {
        // 其中一个任务发生了错误……
    }
@endfinished
```

<a name="running-tasks"></a>
## 运行任务

要运行应用的 `Envoy.blade.php` 文件中定义的任务或故事，可以执行 Envoy 的 `run` 命令，并传入要执行的任务或故事名称。Envoy 会执行该任务，并在运行过程中显示远程服务器的输出：

```shell
php vendor/bin/envoy run deploy
```

<a name="confirming-task-execution"></a>
### 确认任务执行

如果你希望在服务器上运行某个任务前先收到确认提示，可以在任务声明中添加 `confirm` 指令。此选项对于破坏性操作尤其有用：

```blade
@task('deploy', ['on' => 'web', 'confirm' => true])
    cd /home/user/example.com
    git pull origin {{ $branch }}
    php artisan migrate
@endtask
```

<a name="notifications"></a>
## 通知

<a name="slack"></a>
### Slack

Envoy 支持在每个任务执行完毕后向 [Slack](https://slack.com) 发送通知。`@slack` 指令接受一个 Slack Webhook URL 和一个频道名称或用户名。你可以在 Slack 控制面板中创建「Incoming WebHooks」集成，以获取 Webhook URL。

将完整的 Webhook URL 作为 `@slack` 指令的第一个参数，第二个参数则应为频道名称（`#channel`）或用户名（`@user`）：

```blade
@finished
    @slack('webhook-url', '#bots')
@endfinished
```

默认情况下，Envoy 会向通知频道发送一条消息，说明刚刚执行的任务。你也可以向 `@slack` 指令传入第三个参数，用自定义消息覆盖默认消息：

```blade
@finished
    @slack('webhook-url', '#bots', 'Hello, Slack.')
@endfinished
```

<a name="discord"></a>
### Discord

Envoy 也支持在每个任务执行完毕后向 [Discord](https://discord.com) 发送通知。`@discord` 指令接受一个 Discord Webhook URL 和一条消息。你可以在服务器设置中创建一个「Webhook」，并选择该 Webhook 应向哪个频道发送消息，以获取 Webhook URL。将完整的 Webhook URL 传入 `@discord` 指令即可：

```blade
@finished
    @discord('discord-webhook-url')
@endfinished
```

<a name="telegram"></a>
### Telegram

Envoy 也支持在每个任务执行完毕后向 [Telegram](https://telegram.org) 发送通知。`@telegram` 指令接受一个 Telegram Bot ID 和一个 Chat ID。你可以通过 [BotFather](https://t.me/botfather) 创建新机器人来获取 Bot ID，并使用 [@username_to_id_bot](https://t.me/username_to_id_bot) 获取有效的 Chat ID。将完整的 Bot ID 和 Chat ID 传入 `@telegram` 指令即可：

```blade
@finished
    @telegram('bot-id','chat-id')
@endfinished
```

<a name="microsoft-teams"></a>
### Microsoft Teams

Envoy 也支持在每个任务执行完毕后向 [Microsoft Teams](https://www.microsoft.com/en-us/microsoft-teams) 发送通知。`@microsoftTeams` 指令接受 Teams Webhook（必填）、消息、主题颜色（success、info、warning、error）和一个选项数组。你可以创建一个新的 [incoming webhook](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)，以获取 Teams Webhook。Teams API 还提供了许多属性，用于自定义消息框，例如标题、摘要和分区。更多信息请参阅 [Microsoft Teams 文档](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using?tabs=cURL#example-of-connector-message)。将完整的 Webhook URL 传入 `@microsoftTeams` 指令即可：

```blade
@finished
    @microsoftTeams('webhook-url')
@endfinished
```
