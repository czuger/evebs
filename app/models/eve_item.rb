# require 'open-uri'
# # require 'open-uri/cached'
require 'pp'

class EveItem < ApplicationRecord

  # TODO : Use https://github.com/norman/friendly_id
	# To have human readable urls

	extend FriendlyId
	friendly_id :name, use: :slugged

  has_and_belongs_to_many :users
  belongs_to :blueprint

  has_many :blueprint_materials, through: :blueprint
  # has_many :blueprint_components, through: :blueprint_materials, class_name: 'EveItem'
  belongs_to :market_group

  has_many :prices_mins, dependent: :delete_all
  has_many :sales_finals, dependent: :delete_all
  has_many :prices_advices, dependent: :delete_all
  has_many :buy_orders_analytics, dependent: :delete_all

  has_many :public_trade_orders, dependent: :destroy
  has_many :eve_market_histories_groups, :dependent => :delete_all

  has_many :price_advices_min_prices

  has_many :weekly_price_details, dependent: :delete_all

  has_many :group_eve_market_histories

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
  end

  def self.used_items
    used_items, dummy = User.get_used_items_and_trade_hubs
    used_items
  end

  def breadcrumb( view_context )
		return nil unless market_group

    bc = market_group.breadcrumb( view_context )
		bc << Misc::BreadcrumbElement.new( name, view_context.item_url( id ) )
  end

end
