class LoadErrorMailer < ApplicationMailer

  def send_error
    @user = params[:user]
    mail(to: @user[:email], subject: "Erreur de chargement EVEBS sur l'environnement #{Rails.env}") do |format|
      format.text
    end
  end

end
