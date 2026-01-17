from feretui.feretui import FeretUI

def test_feretui_assets_delegation():
    """Test that FeretUI properties delegate to AssetManager."""
    feretui = FeretUI()
    assert feretui.images == feretui.asset_manager.images
    assert feretui.themes == feretui.asset_manager.themes
    assert feretui.fonts == feretui.asset_manager.fonts
    assert feretui.statics == feretui.asset_manager.statics
    assert feretui.css_import == feretui.asset_manager.css_import
    assert feretui.js_import == feretui.asset_manager.js_import
