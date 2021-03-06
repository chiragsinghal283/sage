r"""
Overview of implementation of modular forms for Hecke triangle groups

AUTHORS:
- Jonas Jermann (2013): initial version



Definitions and implementation:
-------------------------------
All classes and functions are also individually documented (with doctest examples).


- **Hecke triangle group:**
  The Von Dyck group corresponding to the triangle group with angles
  ``(pi/2, pi/n, 0)`` for ``n=3, 4, 5, ...``, generated by the conformal
  circle inversion ``S`` and by the translation ``T`` by ``lambda=2*cos(pi/n)``.
  I.e. the subgroup of orientation preserving elements of the triangle
  group generated by reflections along the boundaries of the above hyperbolic
  triangle. The group is arithmetic iff ``n=3, 4, 6, infinity``.

  A (exact) formal expression of the corresponding transfinite diameter ``d``
  (which is used as a formal parameter for Fourier expansion of modular forms)
  can be obtained. For arithmetic groups the (correct) rational number is
  returned instead.

  The group elements correspond to matrices over ZZ[lambda], namely the
  corresponding order in the number field defined by the minimal polynomial
  of lambda (which embedds into ``AlgebraicReal`` accordingly).

  It is possible to check if a given matrix of this form is indeed a member
  of the corresponding ``HeckeTriangleGroup``.

  EXAMPLE::

      sage: from sage.modular.modform_hecketriangle.hecke_triangle_groups import HeckeTriangleGroup
      sage: G = HeckeTriangleGroup(12)
      sage: G
      Hecke triangle group for n = 12
      sage: G.is_arithmetic()
      False
      sage: G.dvalue()
      e^(2*euler_gamma - 2*sqrt(6)*pi/(sqrt(3) + 3) + psi(19/24) + psi(17/24))
      sage: AA(G.lam())
      1.9318516525781...?

      sage: G = HeckeTriangleGroup(6)
      sage: G
      Hecke triangle group for n = 6
      sage: G.is_arithmetic()
      True
      sage: G.dvalue()
      1/108
      sage: AA(G.lam()) == AA(sqrt(3))
      True
      sage: G.gens()
      (
      [ 0 -1]  [  1 lam]
      [ 1  0], [  0   1]
      )
      sage: G.U()^3
      [ lam   -2]
      [   2 -lam]
      sage: G.U().parent()
      Hecke triangle group for n = 6
      sage: G.U().matrix().parent()
      Full MatrixSpace of 2 by 2 dense matrices over Maximal Order in Number Field in lam with defining polynomial x^2 - 3

      sage: G(matrix([[-1, 1+G.lam()],[0, -1]]), check=True)
      Traceback (most recent call last):
      ...
      ValueError: The matrix is not an element of Hecke triangle group for n = 6, up to equivalence it identifies two nonequivalent points.
      sage: G(matrix([[-1, G.lam()],[0, -1]]), check=True)
      [ -1 lam]
      [  0  -1]


- **Analytic type:**
  The analytic type of forms, including the behavior at infinity:

  - Meromorphic (and meromorphic at infinity)
  - Weakly holomorphic (holomorphic and meromorphic at infinity)
  - Holomorphic (and holomorphic at infinity)
  - Cuspidal (holomorphic and zero at infinity)

  Additionally the type specifies whether the form is modular or only quasi modular.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.analytic_type import AnalyticType
      sage: AnalyticType()(["quasi", "cusp"])
      quasi cuspidal


- **Modular form (for Hecke triangle groups):**
  A function of some analytic type which transforms like a modular form
  for the given group, weight ``k`` and multiplier ``epsilon``:

  - ``f(z+lambda) = f(lambda)``
  - ``f(-1/z) = epsilon * (z/i)^k * f(z)``

  The multiplier is either ``1`` or ``-1``.
  The weight is a rational number of the form ``4*(n*l+l')/(n-2) + (1-epsilon)*n/(n-2)``.
  If ``n`` is odd, then the multiplier is unique and given by ``(-1)^(k*(n-2)/2)``.
  The space of modular forms for a given group, weight and multiplier forms a module
  over the base ring. It is finite dimensional if the analytic type is ``holomorphic``.

  Modular forms can be constructed in several ways:

  - Using some already available construction function for modular forms
    (those function are available for all spaces/rings and in general
    do not return elements of the same parent)
  - Specifying the form as a rational function in the basic generators (see below)
  - For weakly holomorphic modular forms it is possible to exactly determine the
    form by specifying (sufficiently many) initial coefficients of its Fourier expansion.
  - There is even hope (no garantuee) to determine a (exact) form from
    the initial numerical coefficients (see below).
  - By specifying the coefficients with respect to a basis of the space
    (if the corresponding space supports coordinate vectors)
  - Arithmetic combination of forms or differential operators applied to forms

  The implementation is based on the implementation of the graded ring (see below).
  All calculations are exact (no precision argument is required).
  The analytic type of forms is checked during construction.
  The analytic type of parent spaces after arithmetic/differential operations
  with elements is changed (extended/reduced) accordingly.

  In particular it is possible to multiply arbitrary modular forms (and end up
  with an element of a modular forms space). If two forms of different
  weight/multiplier are added then an element of the corresponding
  modular forms ring is returned instead.

  Elements of modular forms spaces are represented by their Fourier expansion.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import CuspForms, ModularForms, MeromorphicModularForms
      sage: MeromorphicModularForms(n=4, k=8, ep=1)
      MeromorphicModularForms(n=4, k=8, ep=1) over Integer Ring
      sage: CF = CuspForms(n=7, k=12, ep=1)
      sage: CF
      CuspForms(n=7, k=12, ep=1) over Integer Ring

      sage: MF = ModularForms(k=12, ep=1)
      sage: (x,y,z,d) = MF.pol_ring().gens()

      Using existing functions:
      sage: CF.Delta()
      q + 17/(56*d)*q^2 + 88887/(2458624*d^2)*q^3 + 941331/(481890304*d^3)*q^4 + O(q^5)

      Using rational function in the basic generators:
      sage: MF(x^3)
      1 + 720*q + 179280*q^2 + 16954560*q^3 + 396974160*q^4 + O(q^5)

      Using Fourier expansions:
      sage: qexp = CF.Delta().q_expansion(prec=2)
      sage: qexp
      q + O(q^2)
      sage: qexp.parent()
      Power Series Ring in q over Fraction Field of Univariate Polynomial Ring in d over Integer Ring
      sage: MF(qexp)
      q - 24*q^2 + 252*q^3 - 1472*q^4 + O(q^5)

      Using coordinate vectors:
      sage: MF([0,1]) == MF.f_inf()
      True

      Using arithmetic expressions:
      sage: d = CF.get_d()
      sage: CF.f_rho()^7 / (d*CF.f_rho()^7 - d*CF.f_i()^2) == CF.j_inv()
      True
      sage: MF.E4().serre_derivative() == -1/3 * MF.E6()
      True


- **Hauptmodul:**
  The ``j-function`` for Hecke triangle groups is given by the unique Riemann map
  from the hyperbolic triangle with vertices at ``rho``, ``i`` and ``infinity`` to the
  upper half plane, normalized such that its Fourier coefficients are real and such
  that the first nontrivial Fourier coefficient is 1. The function extends to a
  completely invariant weakly holomorphic function from the upper half plane to the
  complex numbers. Another used normalization (in capital letters) is ``J(i)=1``.
  The coefficients of ``j`` are rational numbers up to a power of ``d=1/j(i)``
  which is only rational in the arithmetic cases ``n=3, 4, 6, infinity``.

  All Fourier coefficients of modular forms are based on the coefficients of ``j``.
  The coefficients of ``j`` are calculated by inverting the Fourier series of its
  inverse (the series inversion is also by far the most expensive operation of all).

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import WeakModularFormsRing
      sage: from sage.modular.modform_hecketriangle.space import WeakModularForms
      sage: WeakModularForms(n=3, k=0, ep=1).j_inv()
      q^-1 + 744 + 196884*q + 21493760*q^2 + 864299970*q^3 + 20245856256*q^4 + O(q^5)
      sage: WeakModularFormsRing(n=7).j_inv()
      f_rho^7/(f_rho^7*d - f_i^2*d)
      sage: WeakModularFormsRing(n=7, red_hom=True).j_inv()
      q^-1 + 151/(392*d) + 165229/(2458624*d^2)*q + 107365/(15059072*d^3)*q^2 + 25493858865/(48358655787008*d^4)*q^3 + 2771867459/(92561489592320*d^5)*q^4 + O(q^5)


- **Basic generators:**
  There exist unique modular forms ``f_rho``, ``f_i`` and ``f_inf`` such that
  each has a simple zero at ``rho=exp(pi/n)``, ``i`` and ``infinity`` resp. and
  no other zeros. The forms are normalized such that their first Fourier coefficient
  is ``1``. They have the weight and multiplier ``(4/(n-2), 1)``, ``(2*n/(n-2), -1)``,
  ``(4*n/(n-2), 1)`` resp. and can be defined in terms of the Hauptmodul ``j``.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import ModularFormsRing
      sage: ModularFormsRing(n=5, red_hom=True).f_rho()
      1 + 7/(100*d)*q + 21/(160000*d^2)*q^2 + 1043/(192000000*d^3)*q^3 + 45479/(1228800000000*d^4)*q^4 + O(q^5)
      sage: ModularFormsRing(n=5, red_hom=True).f_i()
      1 - 13/(40*d)*q - 351/(64000*d^2)*q^2 - 13819/(76800000*d^3)*q^3 - 1163669/(491520000000*d^4)*q^4 + O(q^5)
      sage: ModularFormsRing(n=5, red_hom=True).f_inf()
      q - 9/(200*d)*q^2 + 279/(640000*d^2)*q^3 + 961/(192000000*d^3)*q^4 + O(q^5)
      sage: ModularFormsRing(n=5).f_inf()
      f_rho^5*d - f_i^2*d


- **Eisenstein series and Delta:**
  The Eisenstein series of weight ``2``, ``4`` and ``6`` exist for all ``n`` and
  are all implemented . Note that except for ``n=3`` the series ``E4`` and ``E6``
  do not coincide with ``f_rho`` and ``f_i``.

  Similarly there always exists a (generalization of) ``Delta``. Except for ``n=3``
  it also does not coincide with ``f_inf``.

  In general Eisenstein series of all even weights exist for all ``n``.
  In the non-arithmetic cases they are however very hard to determine
  (it's an open problem(?) and consequently not yet implemented,
  except for trivial one-dimensional cases).

  The Eisenstein series in the arithmetic cases ``n = 3, 4, 6`` are fully
  implemented though. Note that this requires a lot more work/effort
  for ``k != 2, 4, 6`` resp. for multidimensional spaces.

  The case ``n=infinity`` is a special case (since there are two cusps)
  and is not implemented yet.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import ModularFormsRing
      sage: from sage.modular.modform_hecketriangle.space import ModularForms
      sage: ModularFormsRing(n=5).E4()
      f_rho^3
      sage: ModularFormsRing(n=5).E6()
      f_rho^2*f_i
      sage: ModularFormsRing(n=5).Delta()
      f_rho^9*d - f_rho^4*f_i^2*d
      sage: ModularFormsRing(n=5).Delta() == ModularFormsRing(n=5).f_inf()*ModularFormsRing(n=5).f_rho()^4
      True

      The basic generators in some arithmetic cases:
      sage: ModularForms(n=3, k=6).E6()
      1 - 504*q - 16632*q^2 - 122976*q^3 - 532728*q^4 + O(q^5)
      sage: ModularForms(n=4, k=6).E6()
      1 - 56*q - 2296*q^2 - 13664*q^3 - 73976*q^4 + O(q^5)
      sage: ModularForms(n=infinity, k=4).E4()
      1 + 16*q + 112*q^2 + 448*q^3 + 1136*q^4 + O(q^5)

      General Eisenstein series in some arithmetic cases:
      sage: ModularFormsRing(n=4).EisensteinSeries(k=8)
      (-25*f_rho^4 - 9*f_i^2)/(-34)
      sage: ModularForms(n=3, k=12).EisensteinSeries()
      1 + 65520/691*q + 134250480/691*q^2 + 11606736960/691*q^3 + 274945048560/691*q^4 + O(q^5)
      sage: ModularForms(n=6, k=12).EisensteinSeries()
      1 + 6552/50443*q + 13425048/50443*q^2 + 1165450104/50443*q^3 + 27494504856/50443*q^4 + O(q^5)
      sage: ModularForms(n=4, k=22, ep=-1).EisensteinSeries()
      1 - 184/53057489*q - 386252984/53057489*q^2 - 1924704989536/53057489*q^3 - 810031218278584/53057489*q^4 + O(q^5)


- **Generator for ``k=0``, ``ep=-1``:**
  If ``n`` is even then the space of weakly holomorphic modular forms of weight
  ``0`` and multiplier ``-1`` is not empty and generated by one element,
  denoted by ``g_inv``.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import WeakModularForms
      sage: WeakModularForms(n=4, k=0, ep=-1).g_inv()
      q^-1 - 24 - 3820*q - 100352*q^2 - 1217598*q^3 - 10797056*q^4 + O(q^5)
      sage: WeakModularFormsRing(n=8).g_inv()
      f_rho^4*f_i/(f_rho^8*d - f_i^2*d)


- **Quasi modular form (for Hecke triangle groups):**
  ``E2`` no longer transforms like a modular form but like a quasi modular form.
  More generally quasi modular forms are given in terms of modular forms and powers
  of ``E2``. E.g. a holomorphic quasi modular form is a sum of holomorphic modular
  forms multiplied with a power of ``E2`` such that the weights and multipliers match up.
  The space of quasi modular forms for a given group, weight and multiplier forms a
  module over the base ring. It is finite dimensional if the analytic type is
  ``holomorphic``.

  The implementation and construction are analogous to modular forms (see above).
  In particular construction of quasi weakly holomorphic forms by their initial
  Laurent coefficients is supported as well!

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import ModularFormsRing
      sage: from sage.modular.modform_hecketriangle.space import QuasiCuspForms, QuasiModularForms, QuasiWeakModularForms
      sage: QuasiCuspForms(n=7, k=12, ep=1)
      QuasiCuspForms(n=7, k=12, ep=1) over Integer Ring
      sage: QuasiModularForms(n=4, k=8, ep=-1)
      QuasiModularForms(n=4, k=8, ep=-1) over Integer Ring

      sage: QuasiModularForms(n=4, k=2, ep=-1).E2()
      1 - 8*q - 40*q^2 - 32*q^3 - 104*q^4 + O(q^5)

      A quasi weak form can be constructed by using its initial Laurent expansion:
      sage: QF = QuasiWeakModularForms(n=8, k=10/3, ep=-1)
      sage: qexp = (QF.quasi_part_gens(min_exp=-1)[4]).q_expansion(prec=5)
      sage: qexp
      q^-1 - 19/(64*d) - 7497/(262144*d^2)*q + 15889/(8388608*d^3)*q^2 + 543834047/(1649267441664*d^4)*q^3 + 711869853/(43980465111040*d^5)*q^4 + O(q^5)
      sage: qexp.parent()
      Laurent Series Ring in q over Fraction Field of Univariate Polynomial Ring in d over Integer Ring
      sage: QF(qexp).as_ring_element()
      f_rho^3*f_i*E2^2/(f_rho^8*d - f_i^2*d)
      sage: QF(qexp).reduced_parent()
      QuasiWeakModularForms(n=8, k=10/3, ep=-1) over Integer Ring

      Derivatives of (quasi weak) modular forms are again quasi (weak) modular forms:
      sage: CF.f_inf().derivative() == CF.f_inf()*CF.E2()
      True


- **Ring of (quasi) modular forms:**
  The ring of (quasi) modular forms for a given analytic type and Hecke triangle group.
  In fact it is a graded algebra over the base ring where the grading is over
  ``1/(n-2)*Z x Z/(2Z)`` corresponding to the weight and multiplier.
  A ring element is thus a finite linear combination of (quasi) modular forms
  of (possibly) varying weights and multipliers.

  Each ring element is represented as a rational function in the
  generators ``f_rho``, ``f_i`` and ``E2``. The representations and arithmetic
  operations are exact (no precision argument is required).

  Elements of the ring are represented by the rational function in the generators.

  If the parameter ``red_hom`` is set to ``True`` (default: ``False``) then
  operations with homogeneous elements try to return an element of the corresponding
  vector space (if the element is homogeneous) instead of the forms ring.
  It is also easier to use the forms ring with ``red_hom=True`` to construct known
  forms (since then it is not required to specify the weight and multiplier).

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import QuasiModularFormsRing, ModularFormsRing
      sage: QuasiModularFormsRing(n=5, red_hom=True)
      QuasiModularFormsRing(n=5) over Integer Ring
      sage: ModularFormsRing()
      ModularFormsRing(n=3) over Integer Ring
      sage: (x,y,z,d) = ModularFormsRing().pol_ring().gens()

      sage: ModularFormsRing()(x+y)
      f_rho + f_i

      sage: QuasiModularFormsRing(n=5, red_hom=True)(x^5-y^2).reduce()
      1/d*q - 9/(200*d^2)*q^2 + 279/(640000*d^3)*q^3 + 961/(192000000*d^4)*q^4 + O(q^5)


- **Construction of modular forms spaces and rings:**
  There are functorial constructions behind all forms spaces and rings
  which assure that arithmetic operations between those spaces and rings
  work and fit into the coercion framework. In particular ring elements
  are interpreted as constant modular forms in this context and base
  extensions are done if necessary.


- **Fourier expansion of (quasi) modular forms (for Hecke triangle groups):**
  Each (quasi) modular form (in fact each ring element) possesses a Fourier
  expansion of the form ``sum_{n>=n_0} a_n q^n``, where ``n_0`` is an integer,
  ``q=exp(2*pi*i*z/lambda)`` and the coefficients ``a_n`` are rational numbers
  (or more generally an extension of rational numbers) up to a power of ``d``,
  where ``d`` is the (possibly) transcendental parameter described above.
  I.e. the coefficient ring is given by ``Frac(R)(d)``.

  The coefficients are calculated exactly in terms of the (formal) parameter
  ``d``. The expansion is calculated exactly up to the specified precision.
  It is also possible to get a Fourier expansion where ``d`` is evaluated
  to its numerical approximation.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import ModularFormsRing, QuasiModularFormsRing
      sage: ModularFormsRing(n=4).j_inv().q_expansion(prec=3)
      q^-1 + 13/(32*d) + 1093/(16384*d^2)*q + 47/(8192*d^3)*q^2 + O(q^3)
      sage: QuasiModularFormsRing(n=5).E2().q_expansion(prec=3)
      1 - 9/(200*d)*q - 369/(320000*d^2)*q^2 + O(q^3)
      sage: QuasiModularFormsRing(n=5).E2().q_expansion_fixed_d(prec=3)
      1.000000000000... - 6.380956565426...*q - 23.18584547617...*q^2 + O(q^3)


- **Evaluation of forms:**
  (Quasi) modular forms (and also ring elements) can be viewed as
  functions from the upper half plane and can be numerically evaluated
  by using the Fourier expansion.

  The evaluation uses the (quasi) modularity properties (if possible)
  for a faster and more precise evaluation. The precision of the result
  depends both on the numerical precision and on the default precision
  used for the Fourier expansion.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import ModularFormsRing
      sage: f_i = ModularFormsRing(n=4).f_i()
      sage: f_i(i)
      0
      sage: f_i(infinity)
      1
      sage: f_i(1/7 + 0.01*i)
      32189.02016723... + 21226.62951394...*I


- **L-functions of forms:**
  Using the (pari based) function ``Dokchitser`` L-functions of non-constant
  holomorphic modular forms are supported for all values of ``n``.

  Note: For non-arithmetic groups this involves an irrational conductor.
  The conductor for the arithmetic groups ``n = 3, 4, 6, infinity`` is
  ``1, 2, 3, 4`` respectively.

  EXAMPLES::
      sage: from sage.modular.modform.eis_series import eisenstein_series_lseries
      sage: from sage.modular.modform_hecketriangle.space import ModularForms
      sage: f = ModularForms(n=3, k=4).E4()/240
      sage: L = f.lseries()
      sage: L.conductor
      1
      sage: L.check_functional_equation() < 2^(-50)
      True
      sage: L(1)
      -0.0304484570583...
      sage: abs(L(1) - eisenstein_series_lseries(4)(1)) < 2^(-53)
      True
      sage: L.taylor_series(1, 3)
      -0.0304484570583... - 0.0504570844798...*z - 0.0350657360354...*z^2 + O(z^3)
      sage: coeffs = f.q_expansion_vector(min_exp=0, max_exp=20, fix_d=True)
      sage: abs(L(10) - sum([coeffs[k]*k^(-10) for k in range(1,len(coeffs))]).n(53)) < 10^(-7)
      True

      sage: L = ModularForms(n=6, k=6, ep=-1).E6().lseries(num_prec=200)
      sage: L.conductor
      3
      sage: L.check_functional_equation() < 2^(-180)
      True
      sage: L.eps
      -1
      sage: abs(L(3)) < 2^(-180)
      True

      sage: L = ModularForms(n=17, k=12).Delta().lseries()
      sage: L.conductor
      3.86494445880...
      sage: L.check_functional_equation() < 2^(-50)
      True
      sage: L.taylor_series(6, 3)
      2.15697985314... - 1.17385918996...*z + 0.605865993050...*z^2 + O(z^3)

      sage: L = ModularForms(n=infinity, k=2, ep=-1).f_i().lseries()
      sage: L.conductor
      4
      sage: L.check_functional_equation() < 2^(-50)
      True
      sage: L.taylor_series(1, 3)
      0.000000000000... + 5.76543616701...*z + 9.92776715593...*z^2 + O(z^3)


- **(Serre) derivatives:**
  Derivatives and Serre derivatives of forms can be calculated.
  The analytic type is extended accordingly.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import ModularFormsRing
      sage: from sage.modular.modform_hecketriangle.space import QuasiModularForms
      sage: f_inf = ModularFormsRing(n=4, red_hom=True).f_inf()
      sage: f_inf.derivative()/f_inf == QuasiModularForms(n=4, k=2, ep=-1).E2()
      True
      sage: ModularFormsRing().E4().serre_derivative() == -1/3 * ModularFormsRing().E6()
      True


- **Basis for weakly holomorphic modular forms and Faber polynomials:**
  (Natural) generators of weakly holomorphic modular forms can
  be obtained using the corresponding generalized Faber polynomials.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import WeakModularForms, CuspForms
      sage: MF = WeakModularForms(n=5, k=62/3, ep=-1)
      sage: MF.disp_prec(MF._l1+2)

      sage: MF.F_basis(2)
      q^2 - 41/(200*d)*q^3 + O(q^4)
      sage: MF.F_basis(1)
      q - 13071/(640000*d^2)*q^3 + O(q^4)
      sage: MF.F_basis(-0)
      1 - 277043/(192000000*d^3)*q^3 + O(q^4)
      sage: MF.F_basis(-2)
      q^-2 - 162727620113/(40960000000000000*d^5)*q^3 + O(q^4)


- **Basis for quasi weakly holomorphic modular forms:**
  (Natural) generators of quasi weakly holomorphic modular forms can
  also be obtained. In most cases it is even possible to find a basis consisting
  of elements with only one non-trivial Laurent coefficient (up to some coefficient).

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import QuasiWeakModularForms
      sage: QF = QuasiWeakModularForms(n=8, k=10/3, ep=-1)
      sage: QF.default_prec(1)
      sage: QF.quasi_part_gens(min_exp=-1)
      [q^-1 + O(q),
       1 + O(q),
       q^-1 - 9/(128*d) + O(q),
       1 + O(q),
       q^-1 - 19/(64*d) + O(q),
       q^-1 + 1/(64*d) + O(q)]
      sage: QF.default_prec(QF.required_laurent_prec(min_exp=-1))
      sage: QF.q_basis(min_exp=-1)    # long time
      [q^-1 + O(q^5),
       1 + O(q^5),
       q + O(q^5),
       q^2 + O(q^5),
       q^3 + O(q^5),
       q^4 + O(q^5)]


- **Dimension and basis for holomorphic or cuspidal (quasi) modular forms:**
  For finite dimensional spaces the dimension and a basis can be obtained.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import QuasiModularForms
      sage: MF = QuasiModularForms(n=5, k=6, ep=-1)
      sage: MF.dimension()
      3
      sage: MF.default_prec(2)
      sage: MF.gens()
      [1 - 37/(200*d)*q + O(q^2),
       1 + 33/(200*d)*q + O(q^2),
       1 - 27/(200*d)*q + O(q^2)]


- **Coordinate vectors for (quasi) holomorphic modular forms and (quasi) cusp forms:**
  For (quasi) holomorphic modular forms and (quasi) cusp forms it is possible
  to determine the coordinate vectors of elements with respect to the basis.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import ModularForms
      sage: ModularForms(n=7, k=12, ep=1).dimension()
      3
      sage: ModularForms(n=7, k=12, ep=1).Delta().coordinate_vector()
      (0, 1, 17/(56*d))

      sage: from sage.modular.modform_hecketriangle.space import QuasiCuspForms
      sage: MF = QuasiCuspForms(n=7, k=20, ep=1)
      sage: MF.dimension()
      13
      sage: el = MF(MF.Delta()*MF.E2()^4 + MF.Delta()*MF.E2()*MF.E6())
      sage: el.coordinate_vector()    # long time
      (0, 0, 0, 1, 29/(196*d), 0, 0, 0, 0, 1, 17/(56*d), 0, 0)


- **Subspaces:**
  It is possible to construct subspaces of (quasi) holomorphic modular forms
  or (quasi) cusp forms spaces with respect to a specified basis of the
  corresponding ambient space. The subspaces also support coordinate
  vectors with respect to its basis.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.space import ModularForms
      sage: MF = ModularForms(n=7, k=12, ep=1)
      sage: subspace = MF.subspace([MF.E4()^3, MF.Delta()])
      sage: subspace
      Subspace of dimension 2 of ModularForms(n=7, k=12, ep=1) over Integer Ring
      sage: el = subspace(MF.E6()^2)
      sage: el.coordinate_vector()
      (1, -61/(196*d))
      sage: el.ambient_coordinate_vector()
      (1, -61/(196*d), -51187/(614656*d^2))

      sage: from sage.modular.modform_hecketriangle.space import QuasiCuspForms
      sage: MF = QuasiCuspForms(n=7, k=20, ep=1)
      sage: subspace = MF.subspace([MF.Delta()*MF.E2()^2*MF.E4(), MF.Delta()*MF.E2()^4])    # long time
      sage: subspace    # long time
      Subspace of dimension 2 of QuasiCuspForms(n=7, k=20, ep=1) over Integer Ring
      sage: el = subspace(MF.Delta()*MF.E2()^4)    # long time
      sage: el.coordinate_vector()    # long time
      (0, 1)
      sage: el.ambient_coordinate_vector()    # long time
      (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 17/(56*d), 0, 0)


- **Theta subgroup:**
  The Hecke triangle group corresponding to ``n=infinity`` is also
  completely supported. In particular the (special) behavior around
  the cusp ``-1`` is considered and can be specfied.

  EXAMPLES::

      sage: from sage.modular.modform_hecketriangle.graded_ring import QuasiMeromorphicModularFormsRing
      sage: MR = QuasiMeromorphicModularFormsRing(n=infinity, red_hom=True)
      sage: MR
      QuasiMeromorphicModularFormsRing(n=+Infinity) over Integer Ring
      sage: j_inv = MR.j_inv().full_reduce()
      sage: f_i = MR.f_i().full_reduce()
      sage: E4 = MR.E4().full_reduce()
      sage: E2 = MR.E2().full_reduce()

      sage: j_inv
      q^-1 + 24 + 276*q + 2048*q^2 + 11202*q^3 + 49152*q^4 + O(q^5)
      sage: MR.f_rho() == MR(1)
      True
      sage: E4
      1 + 16*q + 112*q^2 + 448*q^3 + 1136*q^4 + O(q^5)
      sage: f_i
      1 - 24*q + 24*q^2 - 96*q^3 + 24*q^4 + O(q^5)
      sage: E2
      1 - 8*q - 8*q^2 - 32*q^3 - 40*q^4 + O(q^5)
      sage: E4.derivative() == E4 * (E2 - f_i)
      True
      sage: f_i.serre_derivative() == -1/2 * E4
      True
      sage: MF = f_i.serre_derivative().parent()
      sage: MF
      ModularForms(n=+Infinity, k=4, ep=1) over Integer Ring
      sage: MF.dimension()
      2
      sage: MF.gens()
      [1 + 240*q^2 + 2160*q^4 + O(q^5), q - 8*q^2 + 28*q^3 - 64*q^4 + O(q^5)]
      sage: E4(i)
      1.941017189...
      sage: E4.order_at(-1)
      1

      sage: MF = (E2/E4).reduced_parent()
      sage: MF.quasi_part_gens(order_1=-1)
      [1 - 40*q + 552*q^2 - 4896*q^3 + 33320*q^4 + O(q^5),
       1 - 24*q + 264*q^2 - 2016*q^3 + 12264*q^4 + O(q^5)]
      sage: prec = MF.required_laurent_prec(order_1=-1)
      sage: qexp = (E2/E4).q_expansion(prec=prec)
      sage: qexp
      1 - 3/(8*d)*q + O(q^2)
      sage: MF.construct_quasi_form(qexp, order_1=-1) == E2/E4
      True
      sage: MF.disp_prec(6)
      sage: MF.q_basis(m=-1, order_1=-1, min_exp=-1)
      q^-1 - 203528/7*q^5 + O(q^6)


- **Determine exact coefficients from numerical ones:**
  There is some experimental support for replacing numerical coefficients with
  corresponding exact coefficients. There is however NO guarantee that
  the procedure will work (and most probably there are cases where it won't).

  EXAMPLES::

     sage: from sage.modular.modform_hecketriangle.space import WeakModularForms, QuasiCuspForms
     sage: WF = WeakModularForms(n=14)
     sage: qexp = WF.J_inv().q_expansion_fixed_d(d_num_prec=1000)
     sage: qexp.parent()
     Laurent Series Ring in q over Real Field with 1000 bits of precision
     sage: qexp_int = WF.rationalize_series(qexp)
     doctest:...: UserWarning: Using an experimental rationalization of coefficients, please check the result for correctness!
     sage: qexp_int.parent()
     Laurent Series Ring in q over Fraction Field of Univariate Polynomial Ring in d over Integer Ring
     sage: qexp_int == WF.J_inv().q_expansion()
     True
     sage: WF(qexp_int) == WF.J_inv()
     True

     sage: QF = QuasiCuspForms(n=8, k=22/3, ep=-1)
     sage: el = QF(QF.f_inf()*QF.E2())
     sage: qexp = el.q_expansion_fixed_d(d_num_prec=1000)
     sage: qexp_int = QF.rationalize_series(qexp)
     sage: qexp_int == el.q_expansion()
     True
     sage: QF(qexp_int) == el
     True



Future ideas:
-------------

- **Define proper spaces (with coordinates) for (quasi) weakly holomorphic forms with bounds on the initial Fourier exponent**

- **Support for general triangle groups (hard)**

- **Support for "congruence" subgroups (hard)**

"""
