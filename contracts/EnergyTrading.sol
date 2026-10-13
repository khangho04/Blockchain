// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EnergyToken.sol";


contract EnergyTrading {

    EnergyToken public immutable token;

    struct Trade {
        address seller;
        address buyer;
        uint256 energyWh;
        uint256 pricePerKwh;
        uint256 totalPrice;
        uint256 timestamp;
    }

    uint256 public tradeCount;

    mapping(uint256 => Trade) public trades;

    event EnergyTraded(
        uint256 indexed tradeId,
        address indexed seller,
        address indexed buyer,
        uint256 energyWh,
        uint256 pricePerKwh,
        uint256 totalPrice,
        uint256 timestamp
    );

    constructor(
        address tokenAddress
    ) {
        token = EnergyToken(tokenAddress);
    }

    function executeTrade(
        address seller,
        address buyer,
        uint256 energyWh,
        uint256 pricePerKwh
    )
        external
    {
        require(
            seller != address(0),
            "Invalid seller"
        );

        require(
            buyer != address(0),
            "Invalid buyer"
        );

        require(
            seller != buyer,
            "Seller and buyer must differ"
        );

        require(
            energyWh > 0,
            "Energy must be greater than zero"
        );

        require(
            pricePerKwh > 0,
            "Price must be greater than zero"
        );

        uint256 totalPrice =
            energyWh *
            pricePerKwh *
            10 ** token.decimals() /
            1000;

        require(
            token.allowance(
                buyer,
                address(this)
            ) >= totalPrice,
            "Insufficient allowance"
        );

        require(
            token.balanceOf(buyer) >= totalPrice,
            "Insufficient token balance"
        );

        bool success = token.transferFrom(
            buyer,
            seller,
            totalPrice
        );

        require(
            success,
            "Token transfer failed"
        );

        uint256 tradeId = tradeCount;

        trades[tradeId] = Trade({
            seller: seller,
            buyer: buyer,
            energyWh: energyWh,
            pricePerKwh: pricePerKwh,
            totalPrice: totalPrice,
            timestamp: block.timestamp
        });

        tradeCount++;

        emit EnergyTraded(
            tradeId,
            seller,
            buyer,
            energyWh,
            pricePerKwh,
            totalPrice,
            block.timestamp
        );
    }

    function getTrade(
        uint256 tradeId
    )
        external
        view
        returns (Trade memory)
    {
        require(
            tradeId < tradeCount,
            "Trade does not exist"
        );

        return trades[tradeId];
    }
}

