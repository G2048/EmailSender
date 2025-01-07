## Email Sender

This is a single microservice that sends emails.

## Requirements

- Docker
- Docker Compose
- Nats broker

## Installation

1. Clone the repository
2. Copy the `env.example` file to `.env`
3. Edit the `.env`
4. Run `docker-compose up -d`
5. Start app: `python -m app.main`

## Usage

1. Choose in your microservice `BROKER_PUBLIC="emails"`
2. NatsClient must be send the `BrokerEmailMessage` model

> [!IMPORTANT]
> You must follow the `BrokerEmailMessage` model protocol

## TODO List

- [ ] Provide a separate interface for broker callback
- [ ] Add tests


## Contributing

Contributions are welcome! If you find a bug or have a suggestion, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
