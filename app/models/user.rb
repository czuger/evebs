require 'digest'

class User < ApplicationRecord

  has_many :blueprint_modifications
  has_many :component_to_buys

  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs

  has_many :regions, through: :trade_hubs
  has_many :blueprints, through: :eve_items
  has_many :blueprint_materials, through: :blueprints
  has_many :blueprint_components, through: :materials
  has_many :user_sale_orders, dependent: :destroy
  has_many :api_key_errors
  has_many :production_lists, dependent: :destroy

  has_many :bpc_assets

  belongs_to :identity, foreign_key: :uid

  has_many :production_list_share_requests, foreign_key: :recipient_id
  has_one :user_pl_share, class_name: 'User', primary_key: :user_pl_share_id, foreign_key: :id

  def self.from_omniauth(auth)
    if auth['provider'] == 'developer'
      raise 'Developer mode is allowed only in test mode' unless Rails.env.test?

      user = where(provider: auth.provider, name: auth.info.name).first_or_initialize
      user.provider = auth.provider
      user.name = auth.info.name
      user.expires_on = Time.now + 3600*24*12*100
      user.save!
    else
      pp auth

      ActiveRecord::Base.transaction do
        user = where(provider: auth['provider'], uid: auth['uid']).first_or_initialize
        user.provider = auth.provider
        user.uid = auth.uid
        user.name = auth.info.name
        user.expires_on = Time.parse(auth.info.expires_on + ' UTC')
        user.token = auth.credentials.token
        user.renew_token = auth.credentials.refresh_token
        user.save!
      end
    end

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
