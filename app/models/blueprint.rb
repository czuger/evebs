class Blueprint < ApplicationRecord
  has_one :eve_item, dependent: :destroy
  has_many :blueprint_materials, dependent: :destroy

  def batch_elements_count
    prod_qtt*nb_runs
  end

end