# Changelog

## [1.1.0](https://github.com/roquerodrigo/ha-midea-dishwasher/compare/v1.0.2...v1.1.0) (2026-08-07)


### Features

* raise a repair issue while the dishwasher stays unreachable ([c06978d](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/c06978d6cb55efc90788c554d7bcb83fb6b66053))
* **sensor:** add a cycle progress percentage sensor ([dbfc9a0](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/dbfc9a01685106351287eb2a456fa68633fcaa46))


### Bug Fixes

* register the action at setup and serialize device commands ([1f321f8](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/1f321f89f58d1a8f10dc475e16be0ed49b3b83e2))
* translate command failures and validate the device identity in credential flows ([868cf0d](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/868cf0d066da791448abb94d1fc2c44eca455313))


### Code Refactoring

* derive every enum option from the library ([4441192](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/4441192e6624948f654d25f875f4faa475731c96))


### Dependencies

* align the SDK manifest pin and refresh the Home Assistant pins ([b1cc280](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/b1cc280b975a9deeab76b242b06a3c4341d860ba))


### Development Dependencies

* **deps-dev:** bump ruff ([faa3f46](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/faa3f467efc5f5368ddebba2a4a6175754ba7a3c))


### Documentation

* describe the current tooling, CI, and repairs behaviour ([cf84788](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/cf84788334051c26be2ea87f934cbfffb1c456ad))
* update CLAUDE.md ([6367eb3](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/6367eb3c9f8b140023388049490f1db33323b5fa))


### Continuous Integration

* assign open issues and pull requests to the repository owner ([584e337](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/584e337fb85b3b4b695b3049c15c8a23326763d3))
* call the shared auto-assign workflow instead of duplicating it ([e680db9](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/e680db971e6af1d1eefc8912904b6bc56f2a2151))
* drop the auto-assign job now handled by its own workflow ([51f489e](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/51f489e54e76645f90c5c8b7741170e7c04352fc))
* drop the blank line left by the removed job ([2bb6e17](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/2bb6e17103968b15b72310605969ddf5dfce7828))
* run checks on pull requests targeting any branch ([ba00eca](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/ba00ecabf2c1b4a1ad4b2760fd8cd10fbe3c9e20))
* run code scanning on pull requests targeting any branch ([ce30e7a](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/ce30e7a70e918d4e1bd1ce1d31b183a9c58d025b))
* split the CI workflow into one file per concern ([4b0e4de](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/4b0e4de8985d56e2adca646c30de1bdccf88e77a))


### Miscellaneous Chores

* Dependabot weekly Mondays 09:00 BRT ([98f1e0e](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/98f1e0e8aeb70b09f603b00f175ea4ff7574c94a))
* **dependabot:** run weekly instead of daily ([c3888f2](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/c3888f27d006d17c39c3fb306c10d180bb113805))
* **dependabot:** run weekly instead of daily ([d503c56](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/d503c56ea64d2609c22f99ef179ec3ac7cdc7100))
* **deps-dev:** bump pre-commit ([81888ab](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/81888ab4ea6bc1a515166abdc7b711f54cf33e8c))
* **deps-dev:** bump ruff to 0.16.0 ([d8ae9c4](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/d8ae9c45e0c55402aa5f1618b81081f309172898))
* **deps-dev:** bump the python-deps group with 2 updates ([160f641](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/160f641178cee0a2fa2c0ac527aa049b667a5cb9))
* **deps-dev:** bump the python-deps group with 2 updates ([bfef10e](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/bfef10e7332f9fad2b051d443fe65a5f5db35dd4))
* **deps-dev:** bump the python-deps group with 2 updates ([75abc56](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/75abc56f6614c2565e17d9c80055962723ed4780))
* **deps:** bump pip from 26.1.1 to 26.1.2 ([7af906a](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/7af906a0951d8744a2131bde9399dff35e7ed51f))
* **deps:** bump pip from 26.1.1 to 26.1.2 ([1f6d8a5](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/1f6d8a56245bfd6bce63d82261a333536b7c7d36))
* lower coverage gate to 90% ([fd75d2e](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/fd75d2e3cc166854ebf043fe86b0612a5c82d285))
* lower coverage gate to 90% ([ea3f062](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/ea3f062fb681e8c904e698ae291d638796ca1d98))
* move CI to the shared workflows repository ([fc53507](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/fc53507622771f09bf943abd65aa8f637ca1e52b))
* release on every conventional commit type ([72a8698](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/72a8698e03c8468b06afa2bfcf005e75b8699306))
* repair the setup script and run lint hooks through uv ([ef9884b](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/ef9884bcf98f082e678b03ad72b89e2000068a17))
* run Dependabot weekly on Mondays at 09:00 (America/Sao_Paulo) ([95a218a](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/95a218ab597c14b60d7b970db842678dff6a09b5))
* run lint commands directly instead of scripts/lint wrapper ([182677b](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/182677bd814bc7c21954fd40668161d0ad0f491d))
* run lint commands directly instead of scripts/lint wrapper, fix stale CODE_STYLE.md ([6dac012](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/6dac0128537c44336421f8accd25304fe7fee576))

## [1.0.2](https://github.com/roquerodrigo/ha-midea-dishwasher/compare/v1.0.1...v1.0.2) (2026-05-25)


### Documentation

* fix CI badge and drop license badge ([e6c905c](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/e6c905cc4d9010f053f60bc76f46b6c9765a91d8))
* fix CI badge and drop license badge ([d5a097b](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/d5a097b8de194c1a57b91d652104f864b9674189))

## [1.0.1](https://github.com/roquerodrigo/ha-midea-dishwasher/compare/v1.0.0...v1.0.1) (2026-05-22)


### Documentation

* standardize CODE_STYLE.md template ([cabfb5f](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/cabfb5f6e603677954c87d8dd4a708e98a082eac))
* standardize CODE_STYLE.md template ([e8d64fd](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/e8d64fd16de09fbb3fb1576e1059c5a6749c6a49))

## [1.0.0](https://github.com/roquerodrigo/ha-midea-dishwasher/compare/v0.1.0...v1.0.0) (2026-05-09)


### Features

* implement Midea dishwasher LAN integration ([70da140](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/70da1402edc3fb01381a13921bedf78ab8e194bf))


### Dependencies

* bump mypy and pytest-homeassistant-custom-component ([23fc89b](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/23fc89b81f2475c62f77e7dcf00820ea07119cf5))


### Documentation

* update README to cover the full entity surface ([430dcbc](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/430dcbc507800c6723dacf84c4d51ef57153c109))


### Miscellaneous Chores

* release 1.0.0 ([65e5d14](https://github.com/roquerodrigo/ha-midea-dishwasher/commit/65e5d14283caace6886f80f9627131cd754a3946))
