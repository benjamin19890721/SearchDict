# Learning 20151106

# Problem

Here is two problems I saw when I wrote validations
**(1) The error message that returned by Rails is not always readable.**

![](resources/E8DE5097-A6B7-458A-99D3-C85C14720363.jpg)

![](resources/FBDA90F0-120C-4327-95F3-955EBD9409DC.jpg)

**(2) Lot of static text stored in the RB files**

```ruby
class AppExtras << ActiveRecord
  # ....
  validates_format_of :ios_team_id, 
                      :with      => /^[A-Za-z0-9]*$/,
                      :if        => Proc.new { |app| !app.ios_team_id.blank? },
                      :allow_nil => true, 
                      :message   => "is invalid. Make sure you only include letters a-z, A-Z and numbers."
                      
  validates_format_of :android_app_sha256_cert_fingerprints, 
                      :with => /^([0-9a-fA-F]{2}:){31}[0-9a-fA-F]{2}$/, 
                      :allow_nil => true,
                      :message => "is an invalid. Make sure the Fingerprint contains \
                                   2-digit 32 hexadecimal-words separated by colon(:)"
  # ...
end
```

# Solution - Valiation and I18n

Rails use the locale file to render the error message (see source code for detail)
https://github.com/rails/rails/blob/master/activemodel/lib/active_model/locale/en.yml

In the locale YAML file 
1) we can give an attributes a label
2) we can define an error message and later refer to this error message by symbol (e.g. :invalid_format)

```yaml
# config/locale/en.yml
en:
  activerecord:
    attributes:
      app_extras:
        ios_team_id: iOS Team ID
        iphone_bundle_id: iPhone Bundle ID
        ipad_bundle_id: iPad Bundle ID
    errors:
      models:
        app_extras:
          attributes:
            iphone_bundle_id:
              invalid_ios_bundle_id: &invalid_ios_bundle_id
                'is invalid. Make sure you only include letters a-z, A-Z, numbers, hiphen(-), underscore(_) or dot(.)'
            ipad_bundle_id:
              invalid_ios_bundle_id: *invalid_ios_bundle_id
  view:
    errors:
      settings_android_app_links:
        disable_update:
          'Navigate to <span class="bold">Settings > Default Redirect Settings</span> and in Android section,
          select <span class="bold"Do you have an Android app?</span> to <span class="bold">Yes</span>'

  # Define errors message that is shared across model/attribtues
  # e.g. validates_format_of :ios_team_id, :with => /^[A-Za-z0-9]*$/, :message => :alphanumeric_only
  errors:
    messages: 
      alphanumeric_only: 'is invalid. Make sure you only include letters a-z, A-Z and numbers.'
```

```yaml
# after refactor
class AppExtras << ActiveRecord
  # ....
  validates_format_of :ios_team_id, 
                      :allow_blank => true,
                      :with        => /^[A-Za-z0-9]*$/,
                      :message     => :alphanumeric_only
  # ...
end
```

We can also did similar thing when we need to render static warning/error message in the view

```ruby
I18n.t('view.errors.settings_android_app_links.disable_update').html_safe
```

```ruby
# Here is some testing code
app_extras = AppExtras.last
app_extras.ios_team_id = '-' 
app_extras.valid? 
app_extras.errors.full_messages
app_extras.errors
```

# Additional Note

If we make any changes to the validation of an exsited attribute, after the release, we need to see whether the current data fit with the new validation.
