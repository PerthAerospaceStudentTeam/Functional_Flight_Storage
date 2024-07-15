#![deny(warnings)]
#![no_main]
#![no_std]

use stm32h7xx_hal::{
    pac,
    xspi::{Qspi, QspiError, QspiMode, QspiWord},
};

enum OPCODES {
    DeviceReset = 0xFF,
    ReadJedecID = 0x9F,
    WriteEnable = 0x06,
    WriteDisable = 0x04,
    ReadRegister = 0x05,
    WriteRegister = 0x1F,
    ProgramLoad = 0x02,
    ProgramExecute = 0x10,
    PageRead = 0x13,
    ReadData = 0x0b,
    EraseBlock = 0xD8,
}

pub struct W25 {
    qspi: Qspi<pac::QUADSPI>,
    ecc: bool,
}

impl W25 {
    pub fn init(mut qspi: Qspi<pac::QUADSPI>) -> W25 {
        //update the block protect pins so that we can actually write to our deivce
        // we want to panic here cause if we dont then we cant actually do anything with our device
        let buffer: u8 = 0b00000000;
        qspi.write_extended(
            QspiWord::U8(OPCODES::WriteRegister as u8),
            QspiWord::U8(0xA0),
            QspiWord::None,
            &[buffer],
        )
        .unwrap();
        W25 { qspi, ecc: true }
    }

    pub fn toggle_ecc(&mut self) -> Result<(), QspiError> {
        // check if chip is free
        if !self.is_busy() {
            let mut buffer: [u8; 1] = [0xF; 1];
            // get current status register
            self.qspi
                .read_extended(
                    QspiWord::U8(OPCODES::ReadRegister as u8),
                    QspiWord::U8(0xB),
                    QspiWord::None,
                    0,
                    &mut buffer,
                )
                .unwrap();

            // update ecc bit to be opposite what it normally is
            let buffer = buffer[0] ^ (1 << 4);

            self.qspi.write_extended(
                QspiWord::U8(OPCODES::WriteRegister as u8),
                QspiWord::U8(0xB0),
                QspiWord::None,
                &[buffer],
            )?;

            self.ecc = !self.ecc;

            Ok(())
        } else {
            // if it isnt raise an error
            Err(QspiError::Busy)
        }
    }

    fn u8_to_bits(&mut self, byte: u8) -> [u8; 8] {
        let mut bits = [0u8; 8];
        for i in 0..8 {
            bits[7 - i] = (byte >> i) & 1;
        }
        bits
    }

    pub fn is_busy(&mut self) -> bool {
        // Default to 1 to say it is busy if something goes wrong when checking status register
        let mut buffer: [u8; 1] = [0xF; 1];
        self.qspi.configure_mode(QspiMode::OneBit).unwrap();
        self.qspi
            .read_extended(
                QspiWord::U8(OPCODES::ReadRegister as u8),
                QspiWord::U8(0xc0),
                QspiWord::None,
                0,
                &mut buffer,
            )
            .unwrap();
        let bits = self.u8_to_bits(buffer[0]);
        // last bit represents our status according to datasheet
        return bits[7] == 1;
    }

    fn check_failed(&mut self) -> bool {
        let mut buffer: [u8; 1] = [0xF; 1];
        self.qspi.configure_mode(QspiMode::OneBit).unwrap();
        self.qspi
            .read_extended(
                QspiWord::U8(OPCODES::ReadRegister as u8),
                QspiWord::U8(0xc0),
                QspiWord::None,
                0,
                &mut buffer,
            )
            .unwrap();
        let write_fail = (buffer[0] >> 3) & 1 == 1;
        let erase_fail = (buffer[0] >> 2) & 1 == 1;

        write_fail || erase_fail
    }

    pub fn enable_write(&mut self) -> Result<(), QspiError> {
        self.qspi.write_extended(
            QspiWord::U8(OPCODES::WriteEnable as u8),
            QspiWord::None,
            QspiWord::None,
            &[],
        )
    }

    pub fn disable_write(&mut self) -> Result<(), QspiError> {
        self.qspi.write_extended(
            QspiWord::U8(OPCODES::WriteDisable as u8),
            QspiWord::None,
            QspiWord::None,
            &[],
        )
    }

    pub fn erase_block(&mut self, addr: u16) -> Result<(), QspiError> {
        self.enable_write()?;
        let _ = self.is_busy();
        self.qspi.write_extended(
            QspiWord::U8(OPCODES::EraseBlock as u8),
            QspiWord::U24(addr.into()),
            QspiWord::None,
            &[],
        )?;

        while self.is_busy() {}
        if self.check_failed() {
            Err(QspiError::Busy)
        } else {
            Ok(())
        }
    }

    pub fn get_id(&mut self) -> Result<[u8; 3], QspiError> {
        let mut buffer: [u8; 3] = [0xFF; 3];
        self.qspi.read_extended(
            QspiWord::U8(OPCODES::ReadJedecID as u8),
            QspiWord::None,
            QspiWord::None,
            8,
            &mut buffer,
        )?;

        Ok(buffer)
    }

    pub fn reset(&mut self) -> () {
        // if our chip cant be reset, panic
        self.qspi
            .write_extended(
                QspiWord::U8(OPCODES::DeviceReset as u8),
                QspiWord::None,
                QspiWord::None,
                &[],
            )
            .unwrap();
    }

    fn load_data(&mut self, column_addr: u16, data: &[u8]) -> Result<(), QspiError> {
        if column_addr > 2112 {
            return Err(QspiError::WordTooLarge);
        }
        self.enable_write()?;
        self.qspi.write_extended(
            QspiWord::U8(OPCODES::ProgramLoad as u8),
            QspiWord::U16(column_addr),
            QspiWord::None,
            &data,
        )?;

        // Wait for write to finish
        while self.is_busy() {}

        //Cleanup
        self.qspi.configure_mode(QspiMode::OneBit)?;

        if self.check_failed() {
            Err(QspiError::Busy)
        } else {
            Ok(())
        }
    }

    fn save_data(&mut self, addr: u16) -> Result<(), QspiError> {
        if addr > 2112 {
            return Err(QspiError::WordTooLarge);
        }
        self.enable_write()?;
        self.qspi.write_extended(
            QspiWord::U8(OPCODES::ProgramExecute as u8),
            QspiWord::U24(addr.into()),
            QspiWord::None,
            &[],
        )?;
        self.disable_write()?;
        while self.is_busy() {}
        if self.check_failed() {
            Err(QspiError::Busy)
        } else {
            Ok(())
        }
    }

    fn load_read(&mut self, page_addr: u16) -> Result<(), QspiError> {
        self.qspi.configure_mode(QspiMode::OneBit)?;
        self.qspi.write_extended(
            QspiWord::U8(OPCODES::PageRead as u8),
            QspiWord::U24(page_addr.into()),
            QspiWord::None,
            &[],
        )?;
        while self.is_busy() {}
        Ok(())
    }

    fn execute_read(&mut self, col_addr: u16) -> Result<[u8; 32], QspiError> {
        let mut buffer: [u8; 32] = [0xFF; 32];
        self.qspi.read_extended(
            QspiWord::U8(OPCODES::ReadData as u8),
            QspiWord::U16(col_addr),
            QspiWord::None,
            8,
            &mut buffer,
        )?;
        self.qspi.configure_mode(QspiMode::OneBit)?;

        Ok(buffer)
    }

    fn find_addr(&mut self, addr: u32) -> (u16, u16) {
        let col_space = if self.ecc { 2048 } else { 2112 };
        let page = addr / col_space;
        let col = addr % col_space;
        // coerce into u16 - this will always succeed as otherwise we wouldn't be able to write to the chip!
        (page.try_into().unwrap(), col.try_into().unwrap())
    }

    pub fn write_byte(&mut self, addr: u32, byte: u8) -> Result<(), QspiError> {
        let (page, col) = self.find_addr(addr);
        self.load_data(col, &[byte])?;
        self.save_data(page)
    }

    pub fn write_data(&mut self, addr: u32, data: &[u8]) -> Result<(), QspiError> {
        let (start_page, start_col) = self.find_addr(addr);
        let pages = data.len() / 2048 + 1;
        // one byte at the end will be our end byte
        let end_bit: u8 = 0xFE;

        for i in 0..pages {
            let start_page_offset = 2048 * i;
            let end_page_offset = (start_page_offset + 2048).min(data.len());
            // split out our data for this segment

            let buf = &data[start_page_offset..end_page_offset];

            // we can only load 32 bytes in at a time
            for j in 0..(buf.len().div_ceil(32)) {
                // if we are in the first loop, write to the given start column
                // otherwise we can safely write at the start of the page
                let col = if i == 0 { start_col } else { 0 };
                let start_data_offset = 32 * j;
                let end_data_offset = (start_data_offset + 32).min(buf.len());
                self.load_data(
                    col + start_data_offset as u16,
                    &buf[start_data_offset..end_data_offset],
                )?;
                self.save_data(start_page + i as u16)?;
            }
        }
        // write our end bit
        self.write_byte(addr + data.len() as u32, end_bit)
    }

    pub fn read_page(&mut self, page_addr: u16) -> Result<[u8; 2048], QspiError> {
        self.load_read(page_addr)?;
        // qspi buffer can only hold 32 bits
        let reads = 2048 / 32;
        // create an array to hold our pagfe
        let mut buf: [u8; 2048] = [0xff; 2048];
        // loop through every subdivision
        for i in 0..reads {
            // grab data
            let data = self.execute_read(32 * i)?;
            // loop through data and set it to our buffer
            for j in 0..data.len() {
                let indexer: usize = <u16 as Into<usize>>::into(i * 32) + j;
                buf[indexer] = data[j];
            }
        }
        Ok(buf)
    }

    pub fn read_byte(&mut self, addr: u32) -> Result<u8, QspiError> {
        let (page, col) = self.find_addr(addr);
        self.load_read(page)?;
        let mut buffer: [u8; 1] = [0xFF; 1];
        self.qspi.read_extended(
            QspiWord::U8(OPCODES::ReadData as u8),
            QspiWord::U16(col),
            QspiWord::None,
            8,
            &mut buffer,
        )?;

        Ok(buffer[0])
    }

    pub fn read_data(&mut self, addr: u32, dest: &mut [u8]) -> Result<(), QspiError> {
        let (start_page, start_col) = self.find_addr(addr);

        let mut eol = false;
        let mut dest_index = 0;
        // only loop through all pages, no more
        for i in 0..=65535 {
            let page = self.read_page(start_page + i)?;
            //offset our col on the first page
            let offset: usize = if i == 0 { start_col.into() } else { 0 };

            for el in &page[offset..page.len()] {
                if *el == 0xfe {
                    eol = true;
                    break;
                } else {
                    if dest_index < dest.len() {
                        dest[dest_index] = *el;
                        dest_index += 1;
                    } else {
                        // break early as our buffer isn't big enough and we wanna break gracefully not panic
                        eol = true;
                        break;
                    }
                }
            }
            // break out of loop if we find our end character
            if eol {
                break;
            }
        }
        Ok(())
    }

    pub fn read_known(&mut self, addr: u32, dest: &mut [u8]) -> Result<(), QspiError> {
        let (start_page, start_col) = self.find_addr(addr);
        let (end_page, _) = self.find_addr(addr + dest.len() as u32);

        let mut dest_index = 0;
        // only loop through the pages our data could take up, no more
        'main: for page in start_page..=end_page {
            // load in our page
            self.load_read(page)?;

            let offset: u16 = if page == 0 { start_col.into() } else { 0 };

            for i in 0..(2048 - offset).div_ceil(32) {
                let page_data = self.execute_read(offset + i * 32)?;

                for &el in &page_data {
                    if dest_index < dest.len() {
                        dest[dest_index] = el;
                        dest_index += 1;
                    } else {
                        break 'main;
                    }
                }
            }
        }
        Ok(())
    }
}
