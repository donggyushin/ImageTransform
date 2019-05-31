"""
Author : Kyungmin Lee (rekyungmin@gmail.com)
Date : 05/29/2019
Descript : Simple asyncio socket server
"""

import socket
import asyncio
import json
import logging
import argparse
import struct
from asyncio import StreamReader, StreamWriter

import command


PORT = 9766


def get_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('8.8.8.8', 1))
            return s.getsockname()[0]

        except OSError:  # unreachable
            return '127.0.0.1'  # localhost


def json_to_dict(data: bytes) -> dict:
    try:
        return json.loads(data.strip())

    except json.decoder.JSONDecodeError:
        return {}


async def read_all(reader: StreamReader, buffer_size=1024, timeout=0.5) -> bytes:
    chunks = []

    raw_len = await reader.read(4)
    if not raw_len:
        logging.info(f'empty raw_size {raw_len!r}')
        return b''

    try:
        json_len = struct.unpack('>I', raw_len)[0]  # unsigned int & big endian
        logging.debug(f'json size: {json_len!r}')
    except struct.error:
        logging.info(f'invalid raw_size {raw_len!r}')
        return b''

    recv_len = 0
    while recv_len < json_len:
        try:
            chunk = await asyncio.wait_for(reader.read(json_len), timeout=timeout)
            chunks.append(chunk)
            recv_len += len(chunk)
        except asyncio.TimeoutError:
            break

    return b''.join(chunks)


async def server_handler(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    logging.info(f'{addr} - received')

    data = await read_all(reader, buffer_size=2048)
    message = b'empty'

    if not data:
        message = b'invalid prefix'
    else:
        request = json_to_dict(data)

        if not request:
            message = b'invalid json data'
        else:
            try:
                message = command.handler(request)
            except Exception as e:
                logging.warning(f'unexpected exception! : {e!r}')
                message = b'unexpected exception'

    message_len = struct.pack('>I', len(message))
    writer.write(message_len)
    writer.write(message)
    await writer.drain()
    writer.close()
    logging.debug(f'{addr} - {message!r}')
    logging.info(f'{addr} - served')


def set_logging(file_name: str, file_level: int = logging.DEBUG, console_level: int = logging.DEBUG):
    logging.basicConfig(level=file_level,
                        format='%(asctime)s %(name)s: %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filename=file_name,
                        filemode='a')

    formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)-8s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)


def main(host: str, port: int):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.start_server(server_handler, host, port, loop=loop))
    logging.info(f'HOST : {host},  PORT : {port}')

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        logging.info(f'KeyboardInterrupt')
        pass

    except Exception as e:
        logging.critical(f'unexpected exception : {e}')

    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    logging.info('SHUTDOWN')


if __name__ == '__main__':
    set_logging('log/server.log', file_level=logging.DEBUG, console_level=logging.DEBUG)

    def port_type(p: str):
        try:
            p = int(p)

        except ValueError:
            raise argparse.ArgumentTypeError(f'"{p}" is not a number')

        if p < 0 or 65535 < p:
            raise argparse.ArgumentTypeError(f'port range : 0 ~ 65535')

        return p

    parser = argparse.ArgumentParser()
    parser.add_argument('-port', '-p', '--port', '--p', type=port_type, help='Enter your port number')
    args = parser.parse_args()
    port = getattr(args, 'port', None) or PORT

    main(get_ip(), port)
