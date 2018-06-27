class Blueprint < ApplicationRecord

  belongs_to :eve_item, dependent: :destroy
  has_many :materials, dependent: :destroy

  def batch_elements_count
    prod_qtt*nb_runs
  end

end