<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
<!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
# Čech Cohomology from Nerves
A small package that computes the Čech cohomology of a good cover of a manifold. <a href="https://github.com/Minstoll/cech-cohomology-tool/blob/main/cech_examples.ipynb">View demo here.</a><br />
Built with:
* [![Python][Python.org]][Python-url]
* [![Jupyter][Jupyter.org]][Jupyter-url]



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#usage">Usage</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
The `cech` package provides tools to compute the Čech cohomology of a finite good cover of a compact manifold. By 'good', we mean that finite intersections of sets in the cover are diffeomorphic to $\mathbb{R}^n.$ <br />
<br />
There exists an isomorphism between the de-Rham cohomology of a manifold and Čech cohomology of any of its good covers, so this is an alternative method to compute the de Rham cohomology of a (compact) manifold.
A good cover always exists for a manifold, and for computational purposes we assume the manifold is compact, in which case there exists a finite good cover, though this may not be trivial to find.<br />
<br />
Concretely, given a finite good cover of a compact manifold, we may construct a dual object: a simplicial complex which we call a 'nerve', wherein 0-simplices correspond to sets, 1-simplices to intersecions of two sets,
2-simplices correspond to intersections of 3 sets and so on. The package provides a suite of tools to encode such a nerve structure, and from this compute the Čech cohomology using combinatorics and linear algebra.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage
The goal is to compute the Čech cohomology of a manifold.
1. <b>Find a good cover</b>: Depending on the manifold, this could be a nontrivial task, and must be carried out manually. The difficulty arises from the requirement for the cover to be good - in particular
that the intersections between sets in the cover are connected. This can be easily overlooked if we first try to cover a related manifold, then identify certain sets to obtain a cover for the desired manifold.
2. <b>Construct nerve structure</b>: From the good cover, label each set using a unique integer. Construct a simplicial complex (effectively an n-dimensional graph made of simplices) such that 1-simplices (edges) correspond to intersections of the sets represented by its boundary elements (vertices), 2-simplices represent intersections between 3 sets, etc. The package provides a suite of methods to streamline the creation of such objects:
   - You could directly enter a dictionary of simplices of every dimension as the first parameter of `Nerve()` during initialization:
     ```py
     n1 = Nerve({0: {"0", "3", "4"}, 1: {"3-4", "0-3"}})
     ```
     Where keys are dimensions and values are sets of names of simplices (they need to be ordered! For example, a 2-simplex with vertices 2, 1 and 3 must be named '1-2-3'). At the moment this does not check whether the simplices in the dictionary form a valid simplicial complex, so this is not recommended.
   - Or, the recommended way is to initialize an empty `Nerve()`, then `.extend()` it with simplices, which will automatically add dependent boundary simplices:
     ```py
     n1 = Nerve()
     s = Simplex("1-0-2")
     n1.extend(s)
     ```
     We can then `print(n1)`:
     ```py
     Nerve({
       0:
           2, 1, 0
       1:
           0-1, 0-2, 1-2
       2:
           0-1-2
     })
     ```
     Note that `Simplex` are initialized with a string representation. Here the order does not matter.
3. <b>Compute the cohomology</b>: Once the nerve has been constructed, we can proceed to compute the Čech cohomology. You can choose to compute the dimension of a specific n-th cohomology group:
   ```py
   n1.cech_cohomology(1)
   ```
   returns `0` for example (n1 is the filled-in triangle nerve defined above); or, compute all potentially non-trivial cohomology group dimensions, from 0 to n inclusive:
   ```py
   n1.cech_cohomology_seq()
   ```
   which returns `1, 0`.
  
Properties of `Simplex` and `Nerve` classes are showcased in <a href="https://github.com/Minstoll/cech-cohomology-tool/blob/main/sanity checks.ipynb">sanity checks.ipynb</a>. For more detailed examples, 
check out the demo notebook: <a href="https://github.com/Minstoll/cech-cohomology-tool/blob/main/cech_examples.ipynb">cech_examples.ipynb</a>.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To install and use the package on your device, follow these instructions:

### Prerequisites

The only non-built-in dependency is `numpy`. In your local environment, run
  ```sh
  python -m pip install numpy
  ```
to install numpy.

### Installation
1. Clone the repo
   ```sh
   git clone https://github.com/Minstoll/cech_cohomology_tool.git
   ```
2. Install the package
   ```sh
   python -m pip install cech
   ```
3. Import the package into your workspace
   ```py
   import cech
   ```
   or
   ```py
   from cech import Nerve, Simplex
   ```
4. Enjoy!
   

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Email - zhing.pu@gmail.com

Project Link: [https://github.com/Minstoll/cech-cohomology-tool](https://github.com/Minstoll/cech-cohomology-tool)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [My supervisor](https://sites.google.com/view/yuhansun)
* [Bott & Tu's textbook](https://books.google.co.uk/books/about/Differential_Forms_in_Algebraic_Topology.html?id=COuPBAAAQBAJ&redir_esc=y)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/Minstoll/cech-cohomology-tool.svg?style=for-the-badge
[issues-url]: https://github.com/Minstoll/cech-cohomology-tool/issues
[license-shield]: https://img.shields.io/github/license/Minstoll/cech-cohomology-tool.svg?style=for-the-badge
[license-url]: https://github.com/Minstoll/cech-cohomology-tool/blob/master/LICENSE
<!-- [linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555 -->
<!-- [linkedin-url]: https://linkedin.com/in/ -->

[Python.org]: https://img.shields.io/badge/Python-123456?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://jquery.com 
[Jupyter.org]: https://img.shields.io/badge/Jupyter-4A4A55?style=for-the-badge&logo=jupyter&logoColor=orange
[Jupyter-url]: https://jquery.com 


