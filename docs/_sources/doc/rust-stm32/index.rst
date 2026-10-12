.. _rust-stm32:

Rust STM32 开发
=========================

一次简单的尝试,不建议比赛时候使用,除非你的队友全是Rust开发者.

rust对于部分国产单片机支持不够好,目前wch、gd、at、py等支持尚可.

当然即使没有对应的hal,你也可以使用svd2rust来生成库文件,简单添加几个unsafe就能用了,但只能进行寄存器级别的操作,
需要手动开启rt feature,否则entry会报错(不知道是不是我没配好).目前还没有找到一个比较好的解决方案,如果有的话欢迎告诉我.

.. toctree::
    rust-stm32
    
.. role:: raw-html(raw)
   :format: html
