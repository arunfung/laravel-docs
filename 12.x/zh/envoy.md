
# Laravel Envoy

-   [简介](#introduction)
-   [安装](#installation)
-   [编写任务](#writing-tasks)
    -   [定义任务](#defining-tasks)
    -   [多服务器](#multiple-servers)
    -   [设置](#setup)
    -   [变量](#variables)
    -   [故事（Stories）](#stories)
    -   [钩子](#completion-hooks)
-   [运行任务](#running-tasks)
    -   [确认任务执行](#confirming-task-execution)
-   [通知](#notifications)
    -   [Slack](#slack)
    -   [Discord](#discord)
    -   [Telegram](#telegram)
    -   [Microsoft Teams](#microsoft-teams)

## 简介

[Laravel Envoy](https://github.com/laravel/envoy?utm_source=chatgpt.com) 是一个在远程服务器上执行常见任务的工具。
使用 [Blade](/docs/laravel/12.x/blade) 风格的语法，你可以很容易地设置部署、运行 Artisan 命令等任务。

目前，Envoy 仅支持 Mac 和 Linux 操作系统。
不过，通过 [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install-win10?utm_source=chatgpt.com)，Windows 也可以获得支持。

## 安装

首先，使用 Composer 包管理器将 Envoy 安装到你的项目中：

```shell
composer require laravel/envoy --dev
```

安装完成后，Envoy 的可执行文件会出现在应用的 `vendor/bin` 目录下：

```shell
php vendor/bin/envoy
```

## 编写任务

### 定义任务

任务（Tasks）是 Envoy 的基本构建块。
任务定义了当被调用时，应该在远程服务器上执行的 shell 命令。

例如，你可以定义一个任务，让它在所有队列工作服务器上执行 `php artisan queue:restart` 命令。

你所有的 Envoy 任务都应该定义在应用根目录的 `Envoy.blade.php` 文件中。
下面是一个示例：

```blade
@servers(['web' => ['user@192.168.1.1'], 'workers' => ['user@192.168.1.2']])

@task('restart-queues', ['on' => 'workers'])
    cd /home/user/example.com
    php artisan queue:restart
@endtask
```



正如你所看到的，在文件顶部定义了一个 `@servers` 数组，这样你就可以在任务声明中通过 `on` 选项来引用这些服务器。
`@servers` 声明必须始终写在同一行上。

在 `@task` 声明中，你应该写入当任务被调用时需要在服务器上执行的 shell 命令。

#### 本地任务（Local Tasks）

你可以通过指定服务器的 IP 地址为 `127.0.0.1` 来强制脚本在本地计算机上运行：

```blade
@servers(['localhost' => '127.0.0.1'])
```

#### 导入 Envoy 任务（Importing Envoy Tasks）

通过使用 `@import` 指令，你可以导入其他 Envoy 文件，这样它们的故事（stories）和任务（tasks）就会被添加到你的文件中。
文件被导入后，你就可以像执行自己 Envoy 文件中定义的任务一样去执行它们：

```blade
@import('vendor/package/Envoy.blade.php')
```

### 多服务器（Multiple Servers）

Envoy 允许你轻松地在多个服务器上运行一个任务。
首先，在 `@servers` 声明中添加额外的服务器。每台服务器都应该分配一个唯一的名称。
定义好额外的服务器后，你就可以在任务的 `on` 数组中列出这些服务器：

```blade
@servers(['web-1' => '192.168.1.1', 'web-2' => '192.168.1.2'])

@task('deploy', ['on' => ['web-1', 'web-2']])
    cd /home/user/example.com
    git pull origin {{ $branch }}
    php artisan migrate --force
@endtask
```

#### 并行执行（Parallel Execution）

默认情况下，任务会在每台服务器上依次（串行）执行。
换句话说，任务会先在第一台服务器运行完成，然后才会继续到第二台服务器。

如果你希望在多台服务器上并行运行任务，可以在任务声明中添加 `parallel` 选项：

```blade
@servers(['web-1' => '192.168.1.1', 'web-2' => '192.168.1.2'])

@task('deploy', ['on' => ['web-1', 'web-2'], 'parallel' => true])
    cd /home/user/example.com
    git pull origin {{ $branch }}
    php artisan migrate --force
@endtask
```



### 设置（Setup）

有时，在运行 Envoy 任务之前，你可能需要执行一些任意的 PHP 代码。
你可以使用 `@setup` 指令来定义一个 PHP 代码块，它会在你的任务运行之前执行：

```php
@setup
    $now = new DateTime;
@endsetup
```

如果你需要在任务执行之前引入其他 PHP 文件，可以在 `Envoy.blade.php` 文件顶部使用 `@include` 指令：

```blade
@include('vendor/autoload.php')

@task('restart-queues')
    # ...
@endtask
```

### 变量（Variables）

如果需要，你可以在调用 Envoy 时，通过命令行向任务传递参数：

```shell
php vendor/bin/envoy run deploy --branch=master
```

在任务中，你可以通过 Blade 的 **“echo” 语法** 来访问这些选项。
你也可以在任务中定义 Blade 的 `if` 语句和循环。

例如，在执行 `git pull` 命令之前，先验证 `$branch` 变量是否存在

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

### 故事（Stories）

Stories 用于将一组任务组合到一个便捷的名称下。
例如，一个 `deploy` 故事可以通过在定义中列出任务名称来依次运行 `update-code` 和 `install-dependencies` 任务：

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

一旦 story 写好，你就可以像调用任务一样来调用它：

```shell
php vendor/bin/envoy run deploy
```



### 钩子（Hooks）

当任务和故事运行时，会触发若干钩子。
Envoy 支持的钩子类型有：`@before`、`@after`、`@error`、`@success` 和 `@finished`。

这些钩子中的所有代码都会被当作 **PHP** 解释并 **在本地执行**，而不是在你的任务所连接的远程服务器上执行。

你可以根据需要定义任意数量的钩子，它们会按照在 Envoy 脚本中出现的顺序依次执行。

#### `@before`

在每个任务执行之前，所有在 Envoy 脚本中注册的 `@before` 钩子都会被执行。
`@before` 钩子会接收即将执行的任务名称：

```blade
@before
    if ($task === 'deploy') {
        // ...
    }
@endbefore
```

#### `@after`

在每个任务执行之后，所有在 Envoy 脚本中注册的 `@after` 钩子都会被执行。
`@after` 钩子会接收刚刚执行完的任务名称：

```blade
@after
    if ($task === 'deploy') {
        // ...
    }
@endafter
```

#### `@error`

在每次任务失败（退出状态码大于 `0`）后，所有在 Envoy 脚本中注册的 `@error` 钩子都会被执行。
`@error` 钩子会接收刚刚执行的任务名称：

```blade
@error
    if ($task === 'deploy') {
        // ...
    }
@enderror
```

#### `@success`

如果所有任务都执行完且没有错误，所有在 Envoy 脚本中注册的 `@success` 钩子都会被执行：

```blade
@success
    // ...
@endsuccess
```

#### `@finished`

在所有任务执行结束后（无论退出状态如何），所有 `@finished` 钩子都会被执行。
`@finished` 钩子会接收已完成任务的退出状态码，该值可能是 `null` 或者一个大于等于 `0` 的整数：

```blade
@finished
    if ($exitCode > 0) {
        // There were errors in one of the tasks...
    }
@endfinished
```



## 运行任务

要运行定义在应用程序 `Envoy.blade.php` 文件中的任务或故事，可以执行 Envoy 的 `run` 命令，并传入你想要执行的任务或故事的名称。
Envoy 会在运行过程中执行该任务，并显示来自远程服务器的输出：

```shell
php vendor/bin/envoy run deploy
```

### 确认任务执行

如果你希望在任务运行到服务器之前进行确认提示，可以在任务声明中加入 `confirm` 指令。
这个选项在执行具有破坏性的操作时尤其有用：

```blade
@task('deploy', ['on' => 'web', 'confirm' => true])
    cd /home/user/example.com
    git pull origin {{ $branch }}
    php artisan migrate
@endtask
```

## 通知

### Slack

Envoy 支持在每个任务执行之后发送通知到 [Slack](https://slack.com?utm_source=chatgpt.com)。
`@slack` 指令接受一个 Slack hook URL 和一个频道/用户名。
你可以在 Slack 控制面板中创建一个 **“Incoming WebHooks” 集成** 来获取你的 webhook URL。

你需要将完整的 webhook URL 作为传给 `@slack` 指令的第一个参数。
第二个参数则是频道名称（如 `#channel`）或用户名（如 `@user`）：

```blade
@finished
    @slack('webhook-url', '#bots')
@endfinished
```

默认情况下，Envoy 通知会向通知频道发送一条消息，说明刚刚执行的任务。
不过，你可以通过向 `@slack` 指令传递第三个参数来自定义消息内容：

```blade
@finished
    @slack('webhook-url', '#bots', 'Hello, Slack.')
@endfinished
```



### Discord

Envoy 也支持在每个任务执行之后发送通知到 [Discord](https://discord.com?utm_source=chatgpt.com)。
`@discord` 指令接受一个 Discord hook URL 和一条消息。

你可以在服务器设置中创建一个 **“Webhook”**，并选择该 Webhook 应该推送到的频道，从而获取你的 webhook URL。
你需要将完整的 Webhook URL 传递给 `@discord` 指令：

```blade
@finished
    @discord('discord-webhook-url')
@endfinished
```

### Telegram

Envoy 也支持在每个任务执行之后发送通知到 [Telegram](https://telegram.org?utm_source=chatgpt.com)。
`@telegram` 指令接受一个 **Telegram Bot ID** 和一个 **Chat ID**。

你可以通过 [BotFather](https://t.me/botfather?utm_source=chatgpt.com) 创建一个新机器人来获取 Bot ID。
你可以通过 [@username_to_id_bot](https://t.me/username_to_id_bot?utm_source=chatgpt.com) 获取有效的 Chat ID。

你需要将完整的 Bot ID 和 Chat ID 传递给 `@telegram` 指令：

```blade
@finished
    @telegram('bot-id','chat-id')
@endfinished
```

### Microsoft Teams

Envoy 也支持在每个任务执行之后发送通知到 [Microsoft Teams](https://www.microsoft.com/en-us/microsoft-teams?utm_source=chatgpt.com)。
`@microsoftTeams` 指令接受：

-   一个 Teams Webhook（必填）
-   一条消息
-   主题颜色（success、info、warning、error）
-   一个选项数组

你可以通过在 Teams 中创建一个新的 [incoming webhook](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?utm_source=chatgpt.com) 来获取你的 Teams Webhook。

Teams API 还支持许多其他属性，用于自定义消息框，例如 **标题**、**摘要** 和 **sections**。
更多信息可以在 [Microsoft Teams 官方文档](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using?tabs=cURL&utm_source=chatgpt.com#example-of-connector-message) 中找到。

你需要将完整的 Webhook URL 传递给 `@microsoftTeams` 指令：

```blade
@finished
    @microsoftTeams('webhook-url')
@endfinished
```
