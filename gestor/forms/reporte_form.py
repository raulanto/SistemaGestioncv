from django import forms
from unfold.widgets import (
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldBooleanWidget
)
from gestor.models.report_avan_model import ReporteAvance


class ReporteAvanceForm(forms.ModelForm):
    class Meta:
        model = ReporteAvance
        fields = "__all__"

        # Aplicamos el estándar 'formula': Reemplazar cada widget nativo por el de Unfold
        widgets = {
            'elemento': UnfoldAdminSelectWidget(),
            'cuadrilla': UnfoldAdminSelectWidget(),
            'reportado_por': UnfoldAdminSelectWidget(),
            'validado_por': UnfoldAdminSelectWidget(),

            # Textos y descripciones
            'descripcion': UnfoldAdminTextareaWidget(
                attrs={'rows': 4, 'placeholder': 'Describa el trabajo realizado...'}),
            'materiales_utilizados': UnfoldAdminTextareaWidget(attrs={'rows': 3}),
            'personal_asignado': UnfoldAdminTextInputWidget(attrs={'placeholder': 'Ej. 5 Albañiles, 1 Cabo'}),

            # Archivos
            'foto': UnfoldAdminFileFieldWidget(),

            # Números (Cantidades y Coordenadas)
            'avance_cantidad': UnfoldAdminDecimalFieldWidget(),
            'avance_porcentaje': UnfoldAdminDecimalFieldWidget(),
            'horas_trabajadas': UnfoldAdminDecimalFieldWidget(),
            'latitud': UnfoldAdminTextInputWidget(attrs={'placeholder': 'Automático desde GPS'}),
            'longitud': UnfoldAdminTextInputWidget(attrs={'placeholder': 'Automático desde GPS'}),

            # Booleanos estilo Switch (Toggle)
            'validado': UnfoldBooleanWidget(),
        }