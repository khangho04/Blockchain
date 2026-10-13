import { network } from "hardhat";


const { ethers } = await network.connect();


async function main() {

    const [
        deployer
    ] = await ethers.getSigners();


    console.log(
        "Deployer:",
        deployer.address
    );


    const EnergyToken =
        await ethers.getContractFactory(
            "EnergyToken"
        );


    const token =
        await EnergyToken.deploy();


    await token.waitForDeployment();


    const tokenAddress =
        await token.getAddress();


    console.log(
        "EnergyToken:",
        tokenAddress
    );


    const EnergyTrading =
        await ethers.getContractFactory(
            "EnergyTrading"
        );


    const trading =
        await EnergyTrading.deploy(
            tokenAddress
        );


    await trading.waitForDeployment();


    const tradingAddress =
        await trading.getAddress();


    console.log(
        "EnergyTrading:",
        tradingAddress
    );
}


main().catch(
    (error) => {

        console.error(error);

        process.exitCode = 1;
    }
);