import { expect } from "chai";
import { network } from "hardhat";


const { ethers } = await network.connect();


describe(
    "Energy Trading",
    function () {

        let token;
        let trading;

        let owner;
        let seller;
        let buyer;


        beforeEach(
            async function () {

                [
                    owner,
                    seller,
                    buyer
                ] = await ethers.getSigners();


                const EnergyToken =
                    await ethers.getContractFactory(
                        "EnergyToken"
                    );

                token =
                    await EnergyToken.deploy();

                await token.waitForDeployment();


                const EnergyTrading =
                    await ethers.getContractFactory(
                        "EnergyTrading"
                    );

                trading =
                    await EnergyTrading.deploy(
                        await token.getAddress()
                    );

                await trading.waitForDeployment();


                const amount =
                    ethers.parseUnits(
                        "100",
                        18
                    );


                await token.transfer(
                    buyer.address,
                    amount
                );
            }
        );


        it(
            "should execute energy trade",
            async function () {

                const energy = 2000;
                const price = 2;

                const total =
                    ethers.parseUnits(
                        "4",
                        18
                    );


                await token
                    .connect(buyer)
                    .approve(
                        await trading.getAddress(),
                        total
                    );


                await trading.executeTrade(
                    seller.address,
                    buyer.address,
                    energy,
                    price
                );


                expect(
                    await token.balanceOf(
                        seller.address
                    )
                ).to.equal(total);


                expect(
                    await token.balanceOf(
                        buyer.address
                    )
                ).to.equal(
                    ethers.parseUnits(
                        "96",
                        18
                    )
                );


                expect(
                    await trading.tradeCount()
                ).to.equal(1);
            }
        );


        it(
            "should store trade information",
            async function () {

                const energy = 2000;
                const price = 2;

                const total =
                    ethers.parseUnits(
                        "4",
                        18
                    );


                await token
                    .connect(buyer)
                    .approve(
                        await trading.getAddress(),
                        total
                    );


                await trading.executeTrade(
                    seller.address,
                    buyer.address,
                    energy,
                    price
                );


                const trade =
                    await trading.getTrade(0);


                expect(
                    trade.seller
                ).to.equal(
                    seller.address
                );


                expect(
                    trade.buyer
                ).to.equal(
                    buyer.address
                );


                expect(
                    trade.energyWh
                ).to.equal(energy);


                expect(
                    trade.pricePerKwh
                ).to.equal(price);


                expect(
                    trade.totalPrice
                ).to.equal(total);
            }
        );


        it(
            "should reject zero energy",
            async function () {

                const amount =
                    ethers.parseUnits(
                        "100",
                        18
                    );


                await token
                    .connect(buyer)
                    .approve(
                        await trading.getAddress(),
                        amount
                    );


                await expect(
                    trading.executeTrade(
                        seller.address,
                        buyer.address,
                        0,
                        2
                    )
                ).to.be.revertedWith(
                    "Energy must be greater than zero"
                );
            }
        );


        it(
            "should reject zero price",
            async function () {

                const amount =
                    ethers.parseUnits(
                        "100",
                        18
                    );


                await token
                    .connect(buyer)
                    .approve(
                        await trading.getAddress(),
                        amount
                    );


                await expect(
                    trading.executeTrade(
                        seller.address,
                        buyer.address,
                        2000,
                        0
                    )
                ).to.be.revertedWith(
                    "Price must be greater than zero"
                );
            }
        );


        it(
            "should reject insufficient balance",
            async function () {

                const total =
                    ethers.parseUnits(
                        "200",
                        18
                    );


                await token
                    .connect(buyer)
                    .approve(
                        await trading.getAddress(),
                        total
                    );


                await expect(
                    trading.executeTrade(
                        seller.address,
                        buyer.address,
                        100000,
                        2
                    )
                ).to.be.revertedWith(
                    "Insufficient token balance"
                );
            }
        );
    }
);