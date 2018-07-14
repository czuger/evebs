require 'digest'

class User < ApplicationRecord

  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs

  has_many :regions, through: :trade_hubs
  has_many :blueprints, through: :eve_items
  has_many :blueprint_materials, through: :blueprints
  has_many :blueprint_components, through: :materials
  has_many :trade_orders
  has_many :api_key_errors
  has_many :production_lists, dependent: :destroy

  has_many :characters
  has_many :bpc_assets, through: :characters

  belongs_to :identity, foreign_key: :uid

  belongs_to :current_character, class_name: 'Character'

  def self.from_omniauth(auth)
    if auth['provider'] == 'developer'
      raise 'Developer mode is allowed only in staging or development mode' unless Rails.env.development? || Rails.env.staging? || Rails.env.test?

      user = where(provider: auth.provider, name: auth.info.name).first_or_initialize
      user.provider = auth.provider
      user.name = auth.info.name
      user.save!

      character = Character.where( user_id: user.id, eve_id: auth.info.name ).first_or_initialize
      character.name = auth.info.name
      character.expires_on = Time.now + 3600*24*12*100
      raise unless character.save!

      user.current_character_id = character.id
      user.save!
    else
      # pp auth

      ActiveRecord::Base.transaction do
        user = where(provider: auth['provider'], uid: auth['uid']).first_or_initialize
        user.provider = auth.provider
        user.uid = auth.uid
        user.name = auth.info.name
        user.save!

        # pp auth

        if auth.info.character_id
          character = Character.where( user_id: user.id, eve_id: auth.info.character_id ).first_or_initialize
          character.name = auth.info.name
          character.expires_on = Time.parse(auth.info.expires_on + ' UTC')
          character.token = auth.credentials.token
          character.renew_token = auth.credentials.refresh_token
          character.save!

          user.current_character_id = character.id
          user.save!
        end
      end
    end

    raise unless user.current_character
    user
  end

  def self.create_with_omniauth(auth)
    create! do |user|
      user.provider = auth['provider']
      user.uid = auth['uid']
      user.name = auth['info']['name']
    end
  end


  def self.get_used_items_and_trade_hubs
    used_item = []
    used_trade_hubs = []
    User.all.to_a.each do |user|
      user.eve_items.each do |eve_item|
        used_item << eve_item unless used_item.include?( eve_item )
      end
      user.trade_hubs.each do |trade_hub|
        used_trade_hubs << trade_hub unless used_trade_hubs.include?( trade_hub )
      end
    end
    [used_item, used_trade_hubs]
  end

  def get_occuped_places
    trade_orders.map{ |to| [to.trade_hub_id,to.eve_item_id] }
  end

end
