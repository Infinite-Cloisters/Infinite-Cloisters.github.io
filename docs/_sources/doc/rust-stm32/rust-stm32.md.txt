# 使用rust开发stm32体验

以下的示例是基于STM32F411的完整demo，需要安装rust相关工具链以及probe-rs

file path >> ./src/main.rs:

```rust
#![no_std]
#![no_main]
#![deny(unsafe_code)]

use stm32f4xx_hal as hal; // memory layout + panic handler
use hal::prelude::*;
use hal::pac;

use cortex_m_rt::entry;
use core::panic::PanicInfo;

#[entry]
fn main() -> ! {
    let dp = pac::Peripherals::take().unwrap();
    let cp  = pac::CorePeripherals::take().unwrap();

    let mut rcc = dp.RCC.constrain();
    let mut delay = cp.SYST.delay(&rcc.clocks);

    let gpioc = dp.GPIOC.split(&mut rcc);
    let mut led = gpioc.pc13.into_push_pull_output();

    loop {
        led.set_low();
        delay.delay_ms(500);
        led.set_high();
        delay.delay_ms(500);
    }
}

#[panic_handler]
fn error_handler(_info: &PanicInfo) -> ! {
    loop {
    }
}

```

file path >> memory.x

```x
MEMORY
{
  RAM     : ORIGIN = 0x20000000,   LENGTH = 128K
  FLASH   : ORIGIN = 0x8000000,   LENGTH = 512K
}

_stack_start = ORIGIN(RAM) + LENGTH(RAM);
```

file path >> Cargo.toml

```toml
[package]
name = "blinky_f411"
version = "0.1.0"
edition = "2024"

[dependencies]
embedded-hal = "1.0"
nb = "1.1"
cortex-m-rt = "0.7"
panic-halt = "1.0"

[dependencies.stm32f4xx-hal]
version = "0.23.0"
features = ["stm32f411"] # replace the model of your microcontroller here
                         # and add other required features
[[bin]]
name = "blinky_f411"
test = false
bench = false

[profile.dev]
panic="unwind"
[profile.release]
panic="unwind"

[build-dependencies]
cc = "1.2"
bindgen = "0.72"
```

file path >> .cargo/config.toml

```toml
[target.thumbv7em-none-eabihf]
runner = "probe-rs download --chip STM32F411CE"

[build]
target = "thumbv7em-none-eabihf"
rustflags = ["-C", "link-arg=-Tlink.x"]
```
