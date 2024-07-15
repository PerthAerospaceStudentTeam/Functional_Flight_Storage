#![deny(warnings)]
#![no_main]
#![no_std]

use cortex_m_rt::entry;
use data::DATA;
use rtt_target::{rprintln, rtt_init_print};
use stm32h7xx_hal::{gpio::Speed, pac, prelude::*, timer};

use panic_rtt_target as _;

use storage_driver::W25;

use core::{
    cell::RefCell,
    sync::atomic::{AtomicU32, Ordering},
};

use cortex_m::interrupt::Mutex;

use pac::interrupt;

static OVERFLOWS: AtomicU32 = AtomicU32::new(0);
static TIMER: Mutex<RefCell<Option<timer::Timer<pac::TIM2>>>> = Mutex::new(RefCell::new(None));

mod data;

#[entry]
fn main() -> ! {
    let mut cp = cortex_m::Peripherals::take().unwrap();
    let dp = pac::Peripherals::take().expect("cannot take peripherals");

    // Constrain and Freeze power
    let pwr = dp.PWR.constrain();
    let pwrcfg = pwr.freeze();

    // Constrain and Freeze clock
    let rcc = dp.RCC.constrain();
    let ccdr = rcc.sys_ck(240.MHz()).freeze(pwrcfg, &dp.SYSCFG);

    rtt_init_print!();

    // Acquire GPIO Pins
    let gpiog = dp.GPIOG.split(ccdr.peripheral.GPIOG);
    let gpiob = dp.GPIOB.split(ccdr.peripheral.GPIOB);
    let gpiod = dp.GPIOD.split(ccdr.peripheral.GPIOD);
    let gpioe = dp.GPIOE.split(ccdr.peripheral.GPIOE);

    // Lock CS
    let _qspi_cs = gpiog.pg6.into_alternate::<10>().speed(Speed::VeryHigh);

    //Lock pins
    let sck = gpiob.pb2.into_alternate().speed(Speed::VeryHigh);
    let io0 = gpiod.pd11.into_alternate().speed(Speed::VeryHigh);
    let io1 = gpiod.pd12.into_alternate().speed(Speed::VeryHigh);
    let io2 = gpioe.pe2.into_alternate().speed(Speed::VeryHigh);
    let io3 = gpiod.pd13.into_alternate().speed(Speed::VeryHigh);

    let mut timer = dp
        .TIM2
        .tick_timer(1.MHz(), ccdr.peripheral.TIM2, &ccdr.clocks);
    timer.listen(timer::Event::TimeOut);

    cortex_m::interrupt::free(|cs| {
        TIMER.borrow(cs).replace(Some(timer));
    });

    unsafe {
        cp.NVIC.set_priority(interrupt::TIM2, 1);
        pac::NVIC::unmask(interrupt::TIM2);
    }

    //Initialize QSPI
    let qspi = dp.QUADSPI.bank1(
        (sck, io0, io1, io2, io3),
        3.MHz(),
        &ccdr.clocks,
        ccdr.peripheral.QSPI,
    );

    let mut w25 = W25::init(qspi);
    // Test 1
    let id = w25.get_id().unwrap();
    rprintln!("Got id: {:x?}", id);
    w25.reset();
    // Test 2 - we need to erase our blocks first
    w25.erase_block(0).unwrap();
    let text = "Hello World!".as_bytes();
    let two_t1 = timestamp();
    w25.write_data(0, text).unwrap();
    let two_t2 = timestamp();
    let mut dest = [0xff; 11];
    let two_t3 = timestamp();
    w25.read_known(0, &mut dest).unwrap();
    let two_t4 = timestamp();
    rprintln!(
        "Write time: {}, Read time: {}",
        two_t2 - two_t1,
        two_t4 - two_t3
    );
    // Test 3 - again, we erase our block first
    w25.erase_block(0).unwrap();
    let three_t1 = timestamp();
    w25.write_data(0, DATA.as_bytes()).unwrap();
    let three_t2 = timestamp();
    let mut dest = [0xff; 40122];
    let three_t3 = timestamp();
    rprintln!("Dest length: {}", dest.len());
    w25.read_known(0, &mut dest).unwrap();
    let three_t4 = timestamp();
    rprintln!("Data: {:?}", &dest[40000..40122]);
    rprintln!("Data length: {}", DATA.as_bytes().len());

    rprintln!(
        "Write time: {}, Read time: {}",
        three_t2 - three_t1,
        three_t4 - three_t3
    );

    loop {
        cortex_m::asm::nop();
    }
}

/// Handle timer overflow and count past 32-bits.
///
/// The interrupt should be configured at maximum priority, it won't take very long.
#[interrupt]
fn TIM2() {
    OVERFLOWS.fetch_add(1, core::sync::atomic::Ordering::SeqCst);
    cortex_m::interrupt::free(|cs| {
        let mut rc = TIMER.borrow(cs).borrow_mut();
        let timer = rc.as_mut().unwrap();
        timer.clear_irq();
    })
}

/// Returns the 64-bit number of microseconds since startup
pub fn timestamp() -> u64 {
    let overflows = OVERFLOWS.load(Ordering::SeqCst) as u64;
    let ctr = cortex_m::interrupt::free(|cs| {
        let rc = TIMER.borrow(cs).borrow();
        let timer = rc.as_ref().unwrap();
        timer.counter() as u64
    });
    (overflows << 32) + ctr
}
