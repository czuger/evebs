class Blueprint < ApplicationRecord

  extend Setup::UpdateBlueprints

  belongs_to :eve_item
  has_many :materials
  validates :eve_item_id, :nb_runs, :prod_qtt, :cpp_blueprint_id, presence: true

  # We don't process some blueprint, because they leads to issues
  UNWANTED_BLUEPRINTS = [3927,34189,34497]

  def batch_elements_count
    prod_qtt*nb_runs
  end

end