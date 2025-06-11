# Changelog

## [0.10.0](https://github.com/code0nwheels/Dwellpy/compare/v0.9.2...v0.10.0) (2025-06-11)


### Features

* add setting for widget unlock threshold ([eeb5a88](https://github.com/code0nwheels/Dwellpy/commit/eeb5a88b096c3fc4397b209d4a8cebe9ef53a73e))
* Standardize widget behavior and add unlock threshold setting ([773f235](https://github.com/code0nwheels/Dwellpy/commit/773f235984106a0696d840f2a5c44d8db6adf8da))


### Bug Fixes

* **ci:** resolve Linux build automation issues ([b62d55a](https://github.com/code0nwheels/Dwellpy/commit/b62d55a6ad43c7c2f9d24949e846929a870f509c))
* hide scroll widget when menu widget expands ([a42c6b7](https://github.com/code0nwheels/Dwellpy/commit/a42c6b7bc14bb50e91167e8b02d3ecf43490a4ed))
* reduce widget unlock thresholds to 150px for better responsiveness ([2126cbc](https://github.com/code0nwheels/Dwellpy/commit/2126cbc25597484940dc0d568a63c6952460d8f2))
* **widget-positioning:** ensure consistent menu widget positioning and locking ([e1a1069](https://github.com/code0nwheels/Dwellpy/commit/e1a1069a28fb3df175124173a85daba5f236b446))

## [0.9.2](https://github.com/code0nwheels/Dwellpy/compare/v0.9.1...v0.9.2) (2025-06-06)


### Bug Fixes

* implement VBScript for silent Windows auto-start with proper quote escaping ([6e34019](https://github.com/code0nwheels/Dwellpy/commit/6e34019345cc99d5fff730ebf7610078975aee8f))

## [0.9.1](https://github.com/code0nwheels/Dwellpy/compare/v0.9.0...v0.9.1) (2025-06-05)


### Bug Fixes

* resolve widget delay and auto-start error handling ([3a59e1e](https://github.com/code0nwheels/Dwellpy/commit/3a59e1e91b861d32469ddc50601f5bee93fcda5d))
* respect widget appearance delay when activating Dwellpy ([6d9ab71](https://github.com/code0nwheels/Dwellpy/commit/6d9ab71efd47e7032938166f353c98324d192e83))
* **ui:** add user-facing error dialogs for Windows auto-start configuration failures ([75f2523](https://github.com/code0nwheels/Dwellpy/commit/75f2523354fc5d585a2f1cc06b15525015de5e1b))

## [0.9.0](https://github.com/code0nwheels/Dwellpy/compare/v0.8.0...v0.9.0) (2025-06-03)


### Features

* trigger release for menu widget and recent improvements ([505da13](https://github.com/code0nwheels/Dwellpy/commit/505da13b515cbe7cf9292a46e5f91b9893a2004b))

## [0.8.0](https://github.com/code0nwheels/Dwellpy/compare/v0.7.1...v0.8.0) (2025-06-02)


### Features

* add taskbar icon support for all PyQt6 windows across all OS ([28193e5](https://github.com/code0nwheels/Dwellpy/commit/28193e51be98e8b5ffcea4d2399d26e41a9f082a))
* release improvements ([#31](https://github.com/code0nwheels/Dwellpy/issues/31)) ([515cea1](https://github.com/code0nwheels/Dwellpy/commit/515cea13d07292171c629de9f5047f244779ab85))


### Bug Fixes

* add tag-based triggering and test mode to PyPI workflow ([ffd30a5](https://github.com/code0nwheels/Dwellpy/commit/ffd30a576094787d303c56cfaff16f2ae06e5ff9))
* remove secrets from release-please ([#32](https://github.com/code0nwheels/Dwellpy/issues/32)) ([dd643a9](https://github.com/code0nwheels/Dwellpy/commit/dd643a98b0281fe1f45d1207f53eeb44d5f2b0ab))

## [0.7.1](https://github.com/code0nwheels/Dwellpy/compare/v0.7.0...v0.7.1) (2025-05-30)


### Bug Fixes

* improve Release Please configuration to create GitHub releases ([93ccb69](https://github.com/code0nwheels/Dwellpy/commit/93ccb6917b40d287133e2cd00fbcdb46bf42c318))

## [0.7.0](https://github.com/code0nwheels/Dwellpy/compare/v0.6.1...v0.7.0) (2025-05-30)


### Features

* add CODEOWNERS file for maintainer-only approval on critical files ([3470b5e](https://github.com/code0nwheels/Dwellpy/commit/3470b5eb01cfe62dca6a8c5e111f4bd13452148f))
* add floating scroll widget ([a600016](https://github.com/code0nwheels/Dwellpy/commit/a6000163323be44e163ccfac5d1e3dd3daff87fe))
* add visible clicks feature with customizable feedback ([d774d5f](https://github.com/code0nwheels/Dwellpy/commit/d774d5f2a969fdd62d63434edb2cada82146e073))
* add visual click feedback with animated circles ([2d44b19](https://github.com/code0nwheels/Dwellpy/commit/2d44b19924229c172498665d03691d91eac303e6))
* integrate PyPI workflow with Release Please automation ([dbf1c72](https://github.com/code0nwheels/Dwellpy/commit/dbf1c72a88e88c29233e0b34f87a95f9d738204c))
* Reorganize project into professional package structure with PyInstaller support ([ac8e426](https://github.com/code0nwheels/Dwellpy/commit/ac8e42686d6cd128e8fa054d5b3a74f74327161c))
* **ui:** add scroll widget settings to configuration dialog ([015edb5](https://github.com/code0nwheels/Dwellpy/commit/015edb5422f9cef7730bc631f588802561b35066))


### Bug Fixes

* configure Release Please to create GitHub releases for PyPI automation ([633198b](https://github.com/code0nwheels/Dwellpy/commit/633198b67fe2dd80c11a53bf67ba23db289de83b))
* correct minimum Python requirement to 3.9+ and clean up documentation ([57c7159](https://github.com/code0nwheels/Dwellpy/commit/57c71592e63f145551efe7587f7916a3b3ca427e))
* ignore clicks on default mode (blue) buttons ([#11](https://github.com/code0nwheels/Dwellpy/issues/11)) ([28c2f55](https://github.com/code0nwheels/Dwellpy/commit/28c2f55b4f6c8b10bcf40d1d6060da098fff4e2d))
* improve UI state feedback when dwell clicker is disabled ([03fe4dc](https://github.com/code0nwheels/Dwellpy/commit/03fe4dc613dc363d66a0f2efc9c0a613dcc188b5))
* Remove conflicting click prevention in ClickManager ([64f568a](https://github.com/code0nwheels/Dwellpy/commit/64f568a158f201be2be10c3b4c02a03d53a5c62c))
* remove invalid release-as field causing parsing error ([537e31c](https://github.com/code0nwheels/Dwellpy/commit/537e31c0c9a468c705bbde67b1108da84369190d))
* **scroll:** stop scrolling when switching between directions ([015edb5](https://github.com/code0nwheels/Dwellpy/commit/015edb5422f9cef7730bc631f588802561b35066))

## [0.6.1](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.6.0...dwellpy-v0.6.1) (2025-05-30)


### Bug Fixes

* correct minimum Python requirement to 3.9+ and clean up documentation ([57c7159](https://github.com/code0nwheels/Dwellpy/commit/57c71592e63f145551efe7587f7916a3b3ca427e))


### Documentation

* add community identity statement to README and wiki ([8d119fa](https://github.com/code0nwheels/Dwellpy/commit/8d119fab978a594612fe6179f8384bd4033c19a8))
* improve placement of community statement in wiki home ([49d7729](https://github.com/code0nwheels/Dwellpy/commit/49d7729b7307883c0ae149160184f46d6d691abe))
* remove incorrect default click setting references and improve troubleshooting ([22e0be2](https://github.com/code0nwheels/Dwellpy/commit/22e0be2c39517037b86726787b6ae2b43a0207bb))

## [0.6.0](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.5.0...dwellpy-v0.6.0) (2025-05-30)


### Features

* add CODEOWNERS file for maintainer-only approval on critical files ([3470b5e](https://github.com/code0nwheels/Dwellpy/commit/3470b5eb01cfe62dca6a8c5e111f4bd13452148f))

## [0.5.0](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.4.0...dwellpy-v0.5.0) (2025-05-29)


### Features

* add visual click feedback with animated circles ([2d44b19](https://github.com/code0nwheels/Dwellpy/commit/2d44b19924229c172498665d03691d91eac303e6))

## [0.4.0](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.3.0...dwellpy-v0.4.0) (2025-05-29)


### Features

* add visible clicks feature with customizable feedback ([d774d5f](https://github.com/code0nwheels/Dwellpy/commit/d774d5f2a969fdd62d63434edb2cada82146e073))

## [0.3.0](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.2.1...dwellpy-v0.3.0) (2025-05-27)


### Features

* integrate PyPI workflow with Release Please automation ([dbf1c72](https://github.com/code0nwheels/Dwellpy/commit/dbf1c72a88e88c29233e0b34f87a95f9d738204c))


### Documentation

* major README restructure with license fixes and platform guidance ([067fe05](https://github.com/code0nwheels/Dwellpy/commit/067fe05b3a7ad2fd3042fe0c66bfe16c44287100))

## [0.2.1](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.2.0...dwellpy-v0.2.1) (2025-05-26)


### Bug Fixes

* ignore clicks on default mode (blue) buttons ([#11](https://github.com/code0nwheels/Dwellpy/issues/11)) ([28c2f55](https://github.com/code0nwheels/Dwellpy/commit/28c2f55b4f6c8b10bcf40d1d6060da098fff4e2d))

## [0.2.0](https://github.com/code0nwheels/Dwellpy/compare/dwellpy-v0.1.0...dwellpy-v0.2.0) (2025-05-26)


### Features

* add floating scroll widget ([a600016](https://github.com/code0nwheels/Dwellpy/commit/a6000163323be44e163ccfac5d1e3dd3daff87fe))
* Reorganize project into professional package structure with PyInstaller support ([ac8e426](https://github.com/code0nwheels/Dwellpy/commit/ac8e42686d6cd128e8fa054d5b3a74f74327161c))
* **ui:** add scroll widget settings to configuration dialog ([015edb5](https://github.com/code0nwheels/Dwellpy/commit/015edb5422f9cef7730bc631f588802561b35066))


### Bug Fixes

* improve UI state feedback when dwell clicker is disabled ([03fe4dc](https://github.com/code0nwheels/Dwellpy/commit/03fe4dc613dc363d66a0f2efc9c0a613dcc188b5))
* Remove conflicting click prevention in ClickManager ([64f568a](https://github.com/code0nwheels/Dwellpy/commit/64f568a158f201be2be10c3b4c02a03d53a5c62c))
* **scroll:** stop scrolling when switching between directions ([015edb5](https://github.com/code0nwheels/Dwellpy/commit/015edb5422f9cef7730bc631f588802561b35066))


### Documentation

* update license to GPL v3 and add version badge ([b59ad99](https://github.com/code0nwheels/Dwellpy/commit/b59ad99f8c4caaa0952a101654c742a3a4bb65c7))

## 0.1.0 (2025-05-23)


### Features

* Reorganize project into professional package structure with PyInstaller support ([ac8e426](https://github.com/code0nwheels/Dwellpy/commit/ac8e42686d6cd128e8fa054d5b3a74f74327161c))


### Bug Fixes

* improve UI state feedback when dwell clicker is disabled ([03fe4dc](https://github.com/code0nwheels/Dwellpy/commit/03fe4dc613dc363d66a0f2efc9c0a613dcc188b5))
* Remove conflicting click prevention in ClickManager ([64f568a](https://github.com/code0nwheels/Dwellpy/commit/64f568a158f201be2be10c3b4c02a03d53a5c62c))
