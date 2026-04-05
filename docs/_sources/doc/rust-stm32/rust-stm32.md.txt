# 使用rust开发stm32体验

以下的示例是基于STM32F411的完整demo，需要安装rust相关工具链以及probe-rs

```powershell
# 我喜欢gnu的工具链
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu
# probe-rs
cargo install probe-rs cargo-flash cargo-embed
# 查看固件大小所要的包
cargo install cargo-binutils
rustup component add llvm-tools-preview
# 查看固件大小，按需使用
cargo size
cargo size -- -A
cargo size --release -- -A
```

file path >> ./src/main.rs:

```rust
#![no_std]
#![no_main]


use stm32f4xx_hal::{self as hal}; // memory layout + panic handler

use hal::prelude::*;
use cortex_m_rt::entry;
use hal::interrupt;

use core::cell::RefCell;
use cortex_m::interrupt::Mutex;

static SERIAL1: Mutex<RefCell<Option<hal::serial::Serial<hal::pac::USART1>>>> = Mutex::new(RefCell::new(None));

// use rtt_target::{rprintln, rtt_init_print};

use defmt_rtt as _;  // 全局日志通道，只需引入
use panic_probe as _; // 可选：panic 时打印 defmt 日志

#[entry]
fn main() -> ! {
    //rtt_init_print!();

    let dp = hal::pac::Peripherals::take().unwrap();
    let cp  = hal::pac::CorePeripherals::take().unwrap();

    let mut rcc = dp.RCC.freeze(hal::rcc::Config::hse(25.MHz()).sysclk(100.MHz()));
    let mut delay = cp.SYST.delay(&rcc.clocks);

    let gpioc = dp.GPIOC.split(&mut rcc);
    let gpioa = dp.GPIOA.split(&mut rcc);

    let mut led = gpioc.pc13.into_push_pull_output();

    let usart1 = dp.USART1;
    let tx_pin = gpioa.pa9;
    let rx_pin = gpioa.pa10;
    let mut serial: hal::serial::Serial<hal::pac::USART1> = hal::serial::Serial::new(
        usart1,
        (tx_pin, rx_pin),
        hal::serial::config::Config::default().baudrate(115_200.bps()),
        &mut rcc,    
    ).unwrap();
        
    unsafe {
        // Enable USART1 interrupt
        hal::pac::NVIC::unmask(hal::pac::Interrupt::USART1);
    }
    serial.listen(hal::serial::Event::RxNotEmpty);

    cortex_m::interrupt::free(|cs| {
        SERIAL1.borrow(cs).replace(Some(serial));
    });

    loop {
        led.set_low();
        delay.delay_ms(500);
        led.set_high();
        delay.delay_ms(500);
    }
}

#[interrupt]
fn USART1() {
    cortex_m::interrupt::free(|cs| {
        if let Some(serial) = SERIAL1.borrow(cs).borrow_mut().as_mut() {
            if let Ok(byte) = serial.read() {
                //rprintln!("Received: {} ('{}')", byte, byte as char);
                defmt::info!("Received: {} ('{}')", byte, byte as char);           // 类似 info!
                // Echo received byte
                let _ = serial.write(byte);
            }
        }
    });
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
cortex-m = { version = "0.7.7", features = ["critical-section-single-core"] }
cortex-m-rt = "0.7"
panic-halt = "1.0"
# rtt-target = "0.6"
defmt = "1.0"
defmt-rtt = "1.1"      # RTT 传输后端
panic-probe = "1.0"    # 可选：panic 时打印 defmt 日志

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
