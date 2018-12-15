Push.create("Welcome cutties !",{
        body: "This is a langing cute page ( QT purpose )",
        icon: 'https://proxy.duckduckgo.com/iu/?u=https%3A%2F%2Fsdl-stickershop.line.naver.jp%2Fproducts%2F0%2F0%2F1%2F1014241%2Fandroid%2Fstickers%2F637249.png%3Bcompress%3Dtrue&f=1',
        timeout: 2000,
        onClick: function () {
            window.focus();
            this.close();
        }
    });
Push.clear();